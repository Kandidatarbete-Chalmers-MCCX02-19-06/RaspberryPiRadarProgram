
# Imports of existing libraries
import time
import threading
import numpy as np
from scipy import signal
import queue

# Import for graphs
import pyqtgraph as pg
from PyQt5 import QtCore

# Imports of our own classes
import filter

# Imports from Acconeer for radar data acquisition
from acconeer_utils.clients.reg.client import RegClient
from acconeer_utils.clients.json.client import JSONClient
from acconeer_utils.clients import configs
from acconeer_utils import example_utils
from acconeer_utils.pg_process import PGProcess, PGProccessDiedException


class DataAcquisition(threading.Thread):
    def __init__(self, list_of_variables_for_threads, bluetooth_server):
        super(DataAcquisition, self).__init__()         # Inherit threading vitals

        # Declaration of global variables
        self.go = list_of_variables_for_threads["go"]
        self.list_of_variables_for_threads = list_of_variables_for_threads
        self.bluetooth_server = bluetooth_server
        self.run_measurement = self.list_of_variables_for_threads['run_measurement']

        # Setup for collecting data from Acconeer's radar files
        self.args = example_utils.ExampleArgumentParser().parse_args()
        example_utils.config_logging(self.args)
        # if self.args.socket_addr:
        #     self.client = JSONClient(self.args.socket_addr)
        #     print("RADAR Port = " + self.args.socket_addr)
        # else:
        #     print("Radar serial port: " + self.args.serial_port)
        #     port = self.args.serial_port or example_utils.autodetect_serial_port()
        #     self.client = RegClient(port)
        self.client = JSONClient('0.0.0.0')
        print("args: " + str(self.args))
        self.client.squeeze = False
        self.config = configs.IQServiceConfig()
        self.config.sensor = self.args.sensors
        print(self.args.sensors)
        #self.config.sensor = 1
        # Settings for radar setup
        self.config.range_interval = [0.4, 1.4]  # Measurement interval
        # Frequency for collecting data. To low means that fast movements can't be tracked.
        self.config.sweep_rate = 40  # Probably 30 is the best, can go up to 100 without graph
        # For use of sample freq in other threads and classes.
        self.list_of_variables_for_threads["sample_freq"] = self.config.sweep_rate
        # The hardware of UART/SPI limits the sweep rate.
        self.config.gain = 0.7  # Gain between 0 and 1. Larger gain increase the SNR, but come at a cost
        # with more instability. Optimally is around 0.7
        self.info = self.client.setup_session(self.config)  # Setup acconeer radar session
        self.data_length = self.info["data_length"]  # Length of data per sample

        # Variables for tracking method
        self.first_data = True      # first time data is processed
        self.dt = 1 / self.list_of_variables_for_threads["sample_freq"]
        self.low_pass_const = self.low_pass_filter_constants_function(0.25, self.dt)  # Constant for a small
        # low-pass filter to smooth the changes. tau changes the filter weight, lower tau means shorter delay.
        # Usually tau = 0.25 is good.
        self.number_of_averages = 2  # Number of averages for tracked peak
        self.plot_time_length = 10  # Length of plotted data
        self.number_of_time_samples = int(self.plot_time_length / self.dt)  # Number of time samples when plotting
        self.max_peak_amplitude = 0
        self.tracked_distance_over_time = np.zeros(self.number_of_time_samples)  # Array for distance over time plot
        self.local_peaks_index = []  # Index of big local peaks
        self.all_local_peaks_index = None  # Index of all, even the smaller local peaks
        self.track_peak_index = []  # Index of last tracked peaks
        self.track_peaks_average_index = None  # Average of last tracked peaks
        self.threshold = 1  # Threshold for removing small local peaks. Start value not important

        # Returned variables
        self.tracked_distance = None  # distance to the tracked peak (m)
        self.tracked_amplitude = None
        self.tracked_phase = None
        self.tracked_data = None  # the final tracked data that is returned

        # Variables for phase to distance and plotting
        self.low_pass_amplitude = None  # low pass filtered amplitude
        self.low_pass_track_peak = None
        self.track_peak_relative_position = None  # used for plotting
        self.relative_distance = 0  # the relative distance that is measured from phase differences (mm)
        self.last_phase = 0  # tracked phase from previous loop
        self.old_relative_distance_values = np.zeros(1000)  # saves old values to remove bias in real time breathing plot
        self.c = 2.998e8  # light speed (m/s)
        self.freq = 60e9  # radar frequency (Hz)
        self.wave_length = self.c / self.freq  # wave length of the radar
        self.delta_distance = 0  # difference in distance between the last two phases (m)
        self.noise_run_time = 0  # number of run times with noise, used to remove noise
        self.not_noise_run_time = 0  # number of run times without noise

        # other
        self.modulo_base = int(self.list_of_variables_for_threads["sample_freq"] / 20)  # how often values are plotted and sent to the app
        if self.modulo_base == 0:
            self.modulo_base = 1
        print('modulo base', self.modulo_base)
        self.run_times = 0  # number of times run in run
        self.calibrating_time = 5  # Time sleep for passing through filters. Used for Real time breathing


        # Graphs
        self.plot_graphs = False  # if plot the graphs or not
        if self.plot_graphs:
            self.pg_updater = PGUpdater(self.config)
            self.pg_process = PGProcess(self.pg_updater)
            self.pg_process.start()
        # acconeer graph
        self.low_pass_vel = 0
        self.hist_vel = np.zeros(self.number_of_time_samples)
        self.hist_pos = np.zeros(self.number_of_time_samples)
        self.last_data = None  # saved old data

        # filter
        self.highpass_HR = filter.Filter('highpass_HR')
        self.lowpass_HR = filter.Filter('lowpass_HR')
        self.highpass_RR = filter.Filter('highpass_RR')
        self.lowpass_RR = filter.Filter('lowpass_RR')

        self.HR_filtered_queue = list_of_variables_for_threads["HR_filtered_queue"]
        self.RR_filtered_queue = list_of_variables_for_threads["RR_filtered_queue"]
        self.RTB_final_queue = list_of_variables_for_threads["RTB_final_queue"]         # TODO remove

    def run(self):
        self.client.start_streaming()  # Starts Acconeers streaming server
        runtimeold=time.time()
        while self.go:
            self.run_times = self.run_times + 1
            #startstart = time.time()
            runtime = time.time()
            print('runtime',(runtime-runtimeold)*1000)
            runtimeold = runtime

            # This data is an 1D array in terminal print, not in Python script however....
            #start = time.time()
            data = self.get_data()
            #done = time.time()
            #print('get_data',(done - start)*1000)
            #start = time.time()
            tracked_data = self.tracking(data)  # processing data and tracking peaks
            #done = time.time()
            #print('tracking', (done - start)*1000)

            # Test with acconeer filter for schmitt.
            if tracked_data is not None:
                #start = time.time()
                #self.RTB_final_queue.put(tracked_data["relative distance"])
                # filter the data
                highpass_filtered_data_HR = self.highpass_HR.filter(
                    tracked_data["relative distance"])
                bandpass_filtered_data_HR = self.lowpass_HR.filter(highpass_filtered_data_HR)
                highpass_filtered_data_RR = self.highpass_RR.filter(
                    tracked_data["relative distance"])  # TODO: Ändra till highpass_filtered
                bandpass_filtered_data_RR = self.lowpass_RR.filter(highpass_filtered_data_RR)

                if not self.run_measurement:
                    calibrating_time = time.time() + self.calibrating_time
                if (self.run_measurement):
                    self.HR_filtered_queue.put(
                       bandpass_filtered_data_HR)  # Put filtered data in output queue to send to SignalProcessing
                    self.RR_filtered_queue.put(bandpass_filtered_data_RR) # TODO Aktivera igen
                    self.RTB_final_queue.put(bandpass_filtered_data_RR)
                    #done = time.time()
                    #print('filter an que', (done - start)*1000)

                    # Send to app
                    #start = time.time()
                    if self.run_times % self.modulo_base == 0:
                        # Send real time breathing amplitude to the app
                        self.bluetooth_server.write_data_to_app(tracked_data["relative distance"], 'real time breath')
                        #self.bluetooth_server.write_data_to_app(
                        #    bandpass_filtered_data_RR, 'real time breath')
                    #done = time.time()
                    #print('send to app', (done - start)*1000)
            if self.plot_graphs and self.run_times % self.modulo_base == 0:
                try:
                    self.pg_process.put_data(tracked_data)  # plot data
                except PGProccessDiedException:
                    self.go.pop(0)
                    break
            #self.run_times_modulo = (self.run_times_modulo + 1) % self.modulo_base
            #donedone = time.time()
            #print('while time',(donedone-startstart)*1000)
        self.RR_filtered_queue.put(0)  # to quit the signal processing thread
        print("out of while go in radar")
        self.client.disconnect()
        self.pg_process.close()

    def get_data(self):
        info, data = self.client.get_next()  # get the next data from the radar
        if info[-1]['sequence_number'] > self.run_times + 10:
            # to remove delay if handling the data takes longer time than for the radar to get it
            print("sequence diff over 10, removing difference",info[-1]['sequence_number']-self.run_times)
            for i in range(0, info[-1]['sequence_number']-self.run_times-1):
                self.client.get_next()  # getting the data without using it
            info, data = self.client.get_next()
            self.run_times = info[-1]['sequence_number']

        return data

    def tracking(self, data):
        data = np.array(data).flatten()
        data_length = len(data)
        amplitude = np.abs(data)
        power = amplitude * amplitude

        # Find and track peaks
        # if np.sum(amplitude)/data_length > 8e-3:
        #     self.noise_run_time = 0
        #     self.not_noise_run_time = self.not_noise_run_time + 1
        # elif self.noise_run_time < 10:
        #     self.noise_run_time = self.noise_run_time + 1

        if np.sum(amplitude)/data_length > 1e-6:
            max_peak_index = np.argmax(power)
            self.max_peak_amplitude = amplitude[max_peak_index]
            if self.first_data:  # first time
                self.track_peak_index.append(max_peak_index)  # global max peak
                self.track_peaks_average_index = max_peak_index
            else:
                self.local_peaks_index, _ = signal.find_peaks(power)  # find local max in data
                self.all_local_peaks_index=self.local_peaks_index
                index = 0
                index_list = []
                for peak in self.local_peaks_index:
                    if np.abs(amplitude[peak]) < self.threshold:
                        index_list.append(index)
                        index += 1
                # deletes all indexes with amplitude < threshold
                np.delete(self.local_peaks_index, index_list)
                if len(self.local_peaks_index) == 0:  # if no large peaks were found, use the latest value instead
                    print("No local peak found")
                    self.track_peak_index.append(self.track_peak_index[-1])
                else:
                    # Difference between found local peaks and last tracked peak
                    peak_difference_index = np.subtract(
                        self.local_peaks_index, self.track_peaks_average_index)
                    # The tracked peak is expected to be the closest local peak found
                    self.track_peak_index.append(
                        self.local_peaks_index[np.argmin(np.abs(peak_difference_index))])
                if len(self.track_peak_index) > self.number_of_averages:
                    self.track_peak_index.pop(0)  # remove oldest value
                if amplitude[self.track_peak_index[-1]] < 0.5 * self.max_peak_amplitude:  # if there is a much larger peak
                    self.track_peak_index.clear()  # reset the array
                    self.track_peak_index.append(max_peak_index)  # new peak is global max
                self.track_peaks_average_index = int(  # Average and smooth the movements of the tracked peak
                    np.round(self.low_pass_const * (np.average(self.track_peak_index))
                             + (1 - self.low_pass_const) * self.track_peaks_average_index))
            # threshold for next peak
            self.threshold = np.abs(amplitude[self.track_peaks_average_index]) * 0.8
            # so it won't follow a much smaller peak
            self.track_peak_relative_position = self.track_peaks_average_index / \
                len(data)  # Position of the peak
            # relative the range of the data
            # Converts relative distance to absolute distance
            self.tracked_distance = (1 - self.track_peaks_average_index / len(data)) * self.config.range_interval[
                0] + self.track_peaks_average_index / len(data) * self.config.range_interval[1]
            # Tracked amplitude is absolute value of data for the tracked index
            #self.tracked_amplitude = np.abs(data[self.track_peaks_average_index])
            self.tracked_amplitude = amplitude[self.track_peaks_average_index] # TODO byt till denna
            # Tracked phase is the angle between I and Q in data for tracked index
            self.tracked_phase = np.angle(data[self.track_peaks_average_index])
        else:
            #track_peak_relative_position = 0
            self.not_noise_run_time = 0
            self.tracked_distance = 0
            self.tracked_phase = 0
            self.tracked_amplitude = 0
            if self.first_data:  # first time
                self.track_peaks_average_index = 0

        # Plots, phase to distance and noise ignoring
        if self.first_data:
            self.tracked_data = None
            self.low_pass_amplitude = amplitude
        else:
            # Amplitude of data for plotting
            self.low_pass_amplitude = self.low_pass_const * amplitude + \
                (1 - self.low_pass_const) * self.low_pass_amplitude

            # real time graph over the whole range
            # self.tracked_distance_over_time = np.roll(
            #     self.tracked_distance_over_time, -1)  # Distance over time
            # self.tracked_distance_over_time[-1] = self.tracked_distance

            # real time graph zoomed in
            # com_idx = int(self.track_peak_relative_position * data_length)
            # delta_angle = np.angle(data[com_idx] * np.conj(self.last_data[com_idx]))
            # vel = self.list_of_variables_for_threads["sample_freq"] * 2.5 * delta_angle / (2 * np.pi)
            # self.low_pass_vel = self.low_pass_const * vel + \
            #     (1 - self.low_pass_const) * self.low_pass_vel
            # dp = self.low_pass_vel / self.list_of_variables_for_threads["sample_freq"]
            # self.hist_pos = np.roll(self.hist_pos, -1)
            # self.hist_pos[-1] = self.hist_pos[-2] + dp
            # plot_hist_pos = self.hist_pos - self.hist_pos.mean()

            plot_hist_pos = None

            # self.RTB_final_queue.put(plot_hist_pos[-1]*10)  # Gets tracked breathing in mm
            # self.RR_filtered_queue.put(plot_hist_pos[-1]*10)

            # Phase to distance and unwrapping
            discount = 2        # TODO optimize for movements
            if self.tracked_phase < -np.pi + discount and self.last_phase > np.pi - discount:
                wrapped_phase = self.tracked_phase + 2 * np.pi
            elif self.tracked_phase > np.pi - discount and self.last_phase < -np.pi + discount:
                wrapped_phase = self.tracked_phase - 2 * np.pi
            else:
                wrapped_phase = self.tracked_phase
            self.delta_distance = self.wave_length * (wrapped_phase - self.last_phase) / (4 * np.pi) * self.low_pass_const + \
                (1 - self.low_pass_const) * self.delta_distance  # calculates the distance traveled from phase differences

            # TODO testa utan lågpassfilter
            #self.delta_distance = self.wave_length * (wrapped_phase - self.last_phase) / (4 * np.pi)

            # TODO testa med konjugat
            #com_idx = int(self.track_peak_relative_position * data_length)
            #print('com_idx',com_idx) samma
            #print('average index',self.track_peaks_average_index)
            com_idx=self.track_peaks_average_index
            delta_angle = np.angle(data[com_idx] * np.conj(self.last_data[com_idx]))
            vel = self.list_of_variables_for_threads["sample_freq"] * 2.5 * delta_angle / (2 * np.pi)
            self.low_pass_vel = self.low_pass_const * vel + \
                (1 - self.low_pass_const) * self.low_pass_vel
            self.delta_distance = self.low_pass_vel / self.list_of_variables_for_threads["sample_freq"] / 1000

            # Don't use the data if only noise were found TODO improve
            # if self.tracked_amplitude < 2e-2 and np.sum(amplitude) / data_length < 1e-2 and self.noise_run_time == 10:
            #     self.delta_distance = 0
            #     if self.relative_distance == 0:
            #         self.old_relative_distance_values = np.zeros(1000)
            # elif self.tracked_amplitude < 1.5e-2 and np.sum(amplitude) / data_length < 1e-2:
            #     self.delta_distance = 0
            #     if self.relative_distance == 0:
            #         self.old_relative_distance_values = np.zeros(1000)
            # if self.not_noise_run_time < 5:
            #     self.delta_distance = 0

            # Remove Noise
            # Indicate if the current measurement is noise or not, to not use the noise in signal_processing
            #print('kvot',self.max_peak_amplitude/(np.sum(amplitude[self.all_local_peaks_index])-self.max_peak_amplitude)*(len(self.all_local_peaks_index)-1))
            if self.max_peak_amplitude < (np.sum(amplitude[self.all_local_peaks_index])-self.max_peak_amplitude)/(len(self.all_local_peaks_index)-1)*2: # np.mean(amplitude[self.all_local_peaks_index])    np.mean(amplitude)
                # Noise
                self.noise_run_time += 1
                if self.noise_run_time >= 10 and self.not_noise_run_time >= 5:
                    self.not_noise_run_time = 0
            else:
                # Real value
                self.not_noise_run_time += 1
                if self.noise_run_time >= 10 and self.not_noise_run_time >= 5:
                    self.noise_run_time = 0
            if self.noise_run_time >= 10 and self.not_noise_run_time < 5:
                # If there has been noise at least 10 times with less than 5 real values, the data is considered to be purely noise.
                self.tracked_distance = 0
                self.delta_distance = 0
                if self.relative_distance == 0: # TODO
                   self.old_relative_distance_values = np.zeros(1000)

            self.relative_distance = self.relative_distance - self.delta_distance  # relative distance in mm
            # The minus sign comes from changing coordinate system; what the radar think is outward is inward for the person that is measured on
            self.last_phase = self.tracked_phase


            # array
            #start = time.time()
            # Code to remove bias that comes from larger movements that is not completely captured by the radar.
            self.old_relative_distance_values = np.roll(self.old_relative_distance_values,-1)
            self.old_relative_distance_values[-1] = self.relative_distance
            self.old_relative_distance_values = self.old_relative_distance_values - self.old_relative_distance_values.mean()/4
            self.relative_distance = self.old_relative_distance_values[-1]
            #end = time.time()
            #print('time diff for list/array',(end-start)*1000)

            # Tracked data to return and plot
            self.tracked_data = {"tracked distance": self.tracked_distance,
                                 "tracked amplitude": self.tracked_amplitude, "tracked phase": self.tracked_phase,
                                 "abs": self.low_pass_amplitude, "tracked distance over time": plot_hist_pos,
                                 "tracked distance over time 2": self.tracked_distance_over_time, "relative distance": self.relative_distance * 1000}
        self.last_data = data
        self.first_data = False
        return self.tracked_data

    # Creates low-pass filter constants for a very small low-pass filter
    def low_pass_filter_constants_function(self, tau, dt):
        return 1 - np.exp(-dt / tau)


class PGUpdater:
    def __init__(self, config):
        self.config = config
        self.interval = config.range_interval

    def setup(self, win):
        win.resize(1600, 1000)
        win.setWindowTitle("Track distance example")

        # Plot amplitude from data and the tracked distance
        self.distance_plot = win.addPlot(row=0, col=0, colspan=2)
        self.distance_plot.showGrid(x=True, y=True)
        self.distance_plot.setLabel("left", "Amplitude")
        self.distance_plot.setLabel("bottom", "Depth (m)")
        self.distance_curve = self.distance_plot.plot(pen=example_utils.pg_pen_cycler(0))
        pen = example_utils.pg_pen_cycler(1)
        pen.setStyle(QtCore.Qt.DashLine)
        self.distance_inf_line = pg.InfiniteLine(pen=pen)
        self.distance_plot.addItem(self.distance_inf_line)

        # Dynamic plot to show breath over time
        # self.distance_over_time_plot = win.addPlot(row=1, col=0)
        # self.distance_over_time_plot.showGrid(x=True, y=True)
        # self.distance_over_time_plot.setLabel("left", "Distance")
        # self.distance_over_time_plot.setLabel("bottom", "Time (s)")
        # self.distance_over_time_curve = self.distance_over_time_plot.plot(
        #     pen=example_utils.pg_pen_cycler(0))
        # self.distance_over_time_plot.setYRange(-8, 8)

        # Plot for tracked distance over time
        # self.distance_over_time_plot2 = win.addPlot(row=1, col=1)
        # self.distance_over_time_plot2.showGrid(x=True, y=True)
        # self.distance_over_time_plot2.setLabel("left", "Distance")
        # self.distance_over_time_plot2.setLabel("bottom", "Time (s)")
        # self.distance_over_time_curve2 = self.distance_over_time_plot2.plot(
        #     pen=example_utils.pg_pen_cycler(0))
        # self.distance_over_time_plot2.setYRange(0.4, 1.5)

        self.smooth_max = example_utils.SmoothMax(self.config.sweep_rate)
        self.first = True

    def update(self, data):
        if self.first:
            self.xs = np.linspace(*self.interval, len(data["abs"]))
            #self.ts = np.linspace(-5, 0, len(data["tracked distance over time"]))
            self.first = False

        self.distance_curve.setData(self.xs, np.array(data["abs"]).flatten())
        self.distance_plot.setYRange(0, self.smooth_max.update(np.amax(data["abs"])))
        if data["tracked distance"] != 0:
            self.distance_inf_line.setValue(data["tracked distance"])
        # else:
        #    self.distance_inf_line.setValue(0.4)
        #self.distance_over_time_curve.setData(self.ts, data["tracked distance over time"])
        #self.distance_over_time_curve2.setData(self.ts, data["tracked distance over time 2"])
