import numpy as np
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
# import scipy as sp
from scipy import signal

from acconeer_utils.clients.reg.client import RegClient
from acconeer_utils.clients.json.client import JSONClient
from acconeer_utils.clients import configs
from acconeer_utils import example_utils


def main():
    args = example_utils.ExampleArgumentParser(num_sens=1).parse_args()
    example_utils.config_logging(args)

    if args.socket_addr:
        client = JSONClient(args.socket_addr)
    else:
        port = args.serial_port or example_utils.autodetect_serial_port()
        client = RegClient(port)

    config = config_setup()
    config.sensor = args.sensors

    tid = 10
    sekvenser = tid * config.sweep_rate
    filename = "Reflektor_2.csv"

    info = client.setup_session(config)
    num_points = info["data_length"]

    amplitude_y_max = 22000
    N_avg = 10
    tracking = Tracking(num_points, config.range_interval, N_avg)
    fig, (amplitude_ax) = plt.subplots(1)
    fig.set_size_inches(12, 6)
    fig.canvas.set_window_title(filename)

    for ax in [amplitude_ax]:
        # ax.set_xlabel("Depth (m)")
        # ax.set_xlim(config.range_interval)
        ax.set_xlabel("Time (s)")
        ax.set_xlim(0, 20)

    amplitude_ax.set_ylabel("tracked distance (m)")
    amplitude_ax.set_ylim(config.range_interval)

    xs = np.linspace(0, 20 * config.sweep_rate, num=N_avg)
    amplitude_line = amplitude_ax.plot(xs, np.zeros_like(xs))[0]

    fig.tight_layout()
    plt.ion()
    plt.show()

    interrupt_handler = example_utils.ExampleInterruptHandler()
    print("Press Ctrl-C to end session")

    client.start_streaming()
    matris = np.zeros((sekvenser, 2))
    counter = 0
    while not interrupt_handler.got_signal:
        info, sweep = client.get_next()
        amplitude = np.abs(sweep)
        track = tracking.tracking(sweep, counter)
        counter += 1
        if counter == num_points:  # change num_points to nmbr of sequences
            counter = 0
        amplitude_line.set_ydata(track)

        if not plt.fignum_exists(1):  # Simple way to check if plot is closed
            break
        fig.canvas.flush_events()
    print("Disconnecting...")
    plt.close()
    client.disconnect()


def config_setup():
    config = configs.EnvelopeServiceConfig()
    # config = configs.IQServiceConfig()
    config.range_interval = [0.4, 0.8]
    config.sweep_rate = 20
    config.gain = 1
    config.session_profile = configs.EnvelopeServiceConfig.MAX_SNR
    return config


class Tracking:
    def __init__(self, num_points, range_interval, N_avg):
        self.N_avg = N_avg
        self.num_points = num_points
        self.config_range_interval = range_interval
        self.I_peaks = np.zeros(self.N_avg)
        self.locks = np.zeros(self.N_avg)
        self.I_peaks_filtered = np.zeros(self.N_avg)
        self.tracked_distance = np.zeros(self.N_avg)
        self.tracked_amplitude = np.zeros(self.N_avg)
        self.tracked_phase=np.zeros(self.N_avg)
        self.data_matrix=np.zeros((1, self.num_points))  # Not even used right now.
        self.threshold=0  # variable for finding peaks above threshold

        # self.data_idx = configs["data_index"]

    def tracking(self, data, data_idx):
        self.data=data
        self.data_idx=data_idx
        counter=0  # Used only for if statement only for first iteration and not when data_idx goes back to zero
        N_avg=self.N_avg  # Number of total peaks to average over
        self.start_distance=0.45  # Initial guess for where
        # self.data_matrix[self.data_idx][:] = self.data
        dist=self.num_points     # number of datapoints in data # self.num_points
        # maximum value
        interval=self.config_range_interval[1] - self.config_range_interval[0]

        matlab_dist=np.linspace(
            self.config_range_interval[0], self.config_range_interval[1], num=dist)

        if self.data_idx == 0:
            self.tracked_distance=np.zeros(self.N_avg)

        self.tracked_amplitude=np.zeros(self.N_avg)
        self.tracked_phase=np.zeros(self.N_avg)

        if self.data_idx == 0 and counter == 0:      # things that only happens first time
            # chooses index closest to starting distance

            distance_in_index=int(round((self.start_distance - self.config_range_interval[0]) / interval * dist))

            # print("dist in idx: ", distance_in_index)
            # I = np.argmax(self.data)
            I=np.argmax(np.abs(self.data))

            self.I_peaks[0]=I
            self.I_peaks_filtered[0] = self.I_peaks[0]
            self.tracked_distance[0]=matlab_dist[int(I)]
            self.tracked_amplitude[0]=np.abs(
                self.data[int(self.I_peaks_filtered[0])])
            self.tracked_phase[0]=np.angle(
                self.data[int(self.I_peaks_filtered[0])])

        # After first seq continous tracking
        else:
            self.locks, _ = signal.find_peaks(np.abs(self.data))
            lista=[]
            for loc in self.locks:
                lista.append(np.abs(self.data[loc]))

            self.locks=[x for x in self.locks if(np.abs(self.data[x]) > self.threshold)]

            Index_in_locks=np.argmin(np.abs(self.locks - self.I_peaks_filtered[self.data_idx - 1]))

            I=self.locks[int(Index_in_locks)]

            if len(self.locks) == 0:
                self.I_peaks[self.data_idx]=self.I_peaks[self.data_idx-1]
            else:
                self.I_peaks[self.data_idx]=I

            if counter == 0:  # Questions about this part.
                self.i_avg_start=np.amax([0, self.data_idx - N_avg])
                if self.data_idx == N_avg:  # change dist to nmbr of sequences later
                    counter=1
            else:
                self.i_avg_start=self.data_idx - N_avg

            self.I_peaks_filtered[self.data_idx]=np.round(np.mean(self.I_peaks[self.i_avg_start:self.data_idx]))

            # determines the amplitude of the last tracked data for find_peaks function
            self.threshold=np.abs(self.data[int(self.I_peaks_filtered[self.data_idx])])*0.5
            self.tracked_distance[self.data_idx]=matlab_dist[int(self.I_peaks_filtered[self.data_idx])]
            self.tracked_amplitude[self.data_idx]=np.abs(self.data[int(self.I_peaks_filtered[self.data_idx])])
            self.tracked_phase[self.data_idx]=np.angle(self.data[int(self.I_peaks_filtered[self.data_idx])])
        return self.tracked_distance


if __name__ == "__main__":
    main()
