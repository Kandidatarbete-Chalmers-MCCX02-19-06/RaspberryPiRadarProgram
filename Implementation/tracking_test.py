import numpy as np
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
# import scipy as sp
from scipy import signal
import time

from acconeer_utils.clients.reg.client import RegClient
from acconeer_utils.clients.json.client import JSONClient
from acconeer_utils.clients import configs
from acconeer_utils import example_utils
from acconeer_utils.mpl_process import PlotProcess, PlotProccessDiedException, FigureUpdater


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
    print("numpoints: ", num_points)
    fig, (amplitude_ax) = plt.subplots(1)
    fig.set_size_inches(12, 6)
    fig.canvas.set_window_title(filename)

    for ax in [amplitude_ax]:
        # ax.set_xlabel("Depth (m)")
        # ax.set_xlim(config.range_interval)
        ax.set_xlabel("Time (s)")
        ax.set_xlim(0, 100)

    # amplitude_ax.set_ylabel("Amplitude")
    # amplitude_ax.set_ylim(0, 1.1 * amplitude_y_max)

    amplitude_ax.set_ylabel("tracked distance (m)")
    amplitude_ax.set_ylim(config.range_interval)

    xs = np.linspace(0, 100, num=100)
    amplitude_line = amplitude_ax.plot(xs, np.zeros_like(xs))[0]

    fig.tight_layout()
    plt.ion()
    plt.show()
    list = np.zeros(100)
    i = 0
    interrupt_handler = example_utils.ExampleInterruptHandler()
    print("Press Ctrl-C to end session")

    client.start_streaming()
    matris = np.zeros((sekvenser, 2))
    counter = 0
    while not interrupt_handler.got_signal:
        # for i in range(0, sekvenser):
        info, sweep = client.get_next()
        start = round(time.time()*1000)/1000
        track = tracking.tracking(sweep)
        end = round(time.time()*1000)/1000
        print("Time for tracking loop {}".format(end-start))
        list[i] = track
        amplitude_line.set_ydata(list)

        i += 1
        if i == 100:
            i = 0
            list = np.zeros(100)
        if not plt.fignum_exists(1):  # Simple way to check if plot is closed
            break
        fig.canvas.flush_events()
        # annotate.remove()
    # matris = np.mean(matris, axis=0)
    # np.savetxt(filename, matris, delimiter=",")

    print("Disconnecting...")
    plt.close()
    client.disconnect()


def config_setup():
    config = configs.EnvelopeServiceConfig()
    # config = configs.IQServiceConfig()
    config.range_interval = [0.4, 0.8]
    config.sweep_rate = 4
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
        self.tracked_phase = np.zeros(self.N_avg)
        self.threshold = 0  # variable for finding peaks above threshold
        self.data_idx = 0
        self.real_dist = np.linspace(self.config_range_interval[0], self.config_range_interval[1], num=self.num_points)     # converts index to real length
        self.counter = 0  # Used only for if statement only for first iteration and not when data_idx goes back to zero

    def tracking(self, data):
        self.data = data

        if self.data_idx == 0 and self.counter == 0:      # things that only happens first time
            I = np.argmax(np.abs(self.data))
            self.I_peaks[0:(self.N_avg)] = I
            self.I_peaks_filtered[0] = self.I_peaks[0]
            self.tracked_distance[0] = self.real_dist[int(self.I_peaks_filtered[0])]
            self.tracked_amplitude[0] = np.abs(self.data[int(self.I_peaks_filtered[0])])
            self.tracked_phase[0] = np.angle(self.data[int(self.I_peaks_filtered[0])])

        # After first seq continous tracking
        else:
            self.locks, _ = signal.find_peaks(np.abs(self.data))        # find local maximas in data
            self.locks = [x for x in self.locks if(np.abs(self.data[x]) > self.threshold)]      # removes local maxima if under threshhold
            difference = np.subtract(self.locks, self.I_peaks_filtered[self.data_idx])
            print("locks: ", self.locks)
            print("Last I_peaks_filtered: ", self.I_peaks_filtered[self.data_idx])
            print("difference: ", difference)
            abs = np.abs(difference)
            print("abs: ", abs)
            argmin = np.argmin(abs)
            print("argmin: ", argmin)
            Index_in_locks = argmin

            # Index_in_locks = np.argmin(np.abs(self.locks - self.I_peaks_filtered[self.data_idx - 1]))       # difference between current peak index and last peak index

            if len(self.locks) == 0:        # if no peak is found
                self.I_peaks[self.data_idx] = self.I_peaks[self.data_idx - 1]
                print("Last value. Not updated.")
            else:
                I = self.locks[int(Index_in_locks)]
                self.I_peaks[self.data_idx] = I

            #print("Locks: ", self.locks)
            print("I_peaks: ", self.I_peaks)

            # if self.counter == 0:  # Questions about this part.
            #     self.i_avg_start = 0        # this will be 0 as long as counter == 0
            #     if self.data_idx == self.N_avg - 1:  # change dist to nmbr of sequences later
            #         self.counter = 1
            # else:
            # self.i_avg_start = self.data_idx - (self.N_avg - 1)

            self.I_peaks_filtered[self.data_idx] = np.round(np.mean(self.I_peaks))      # mean value of N_avg latest peaks

            self.threshold = np.abs(self.data[int(self.I_peaks_filtered[self.data_idx])])*0.5       # determines threshold
            self.tracked_distance[self.data_idx] = self.real_dist[int(self.I_peaks_filtered[self.data_idx])]
            self.tracked_amplitude[self.data_idx] = np.abs(self.data[int(self.I_peaks_filtered[self.data_idx])])
            self.tracked_phase[self.data_idx] = np.angle(self.data[int(self.I_peaks_filtered[self.data_idx])])

        # print("I_peaks_filtered: ", self.I_peaks_filtered)

        self.data_idx += 1
        if self.data_idx == self.N_avg:
            self.data_idx = 0
        return self.tracked_distance[self.data_idx - 1]

if __name__ == "__main__":
    main()
