import time
import threading
import numpy as np
from scipy import signal
import queue

import pyqtgraph as pg
from PyQt5 import QtCore

from acconeer_utils.clients.reg.client import RegClient
from acconeer_utils.clients.json.client import JSONClient
from acconeer_utils.clients import configs
from acconeer_utils import example_utils
from acconeer_utils.pg_process import PGProcess, PGProccessDiedException


class DataAcquisition(threading.Thread):
    def __init__(self, go):
        super(DataAcquisition, self).__init__()  # Inherit threading vitals
        self.go = go
        # Setup for collecting data from acconeers radar files.
        self.args = example_utils.ExampleArgumentParser().parse_args()
        example_utils.config_logging(self.args)
        if self.args.socket_addr:
            self.client = JSONClient(self.args.socket_addr)
            # Test för att se vilken port som används av radarn
            print("RADAR Port = " + self.args.socket_addr)
        else:
            port = self.args.serial_port or example_utils.autodetect_serial_port()
            self.client = RegClient(port)
        self.client.squeeze = False
        self.config = configs.IQServiceConfig()
        self.config.sensor = self.args.sensors
        # Settings for radar setup
        self.config.range_interval = [0.4, 1.5]  # Measurement interval
        self.config.sweep_rate = 10  # Frequency for collecting data
        self.config.gain = 0.7  # Gain between 0 and 1.

        # för plotten
        self.pg_updater = PGUpdater(self.config)
        self.pg_process = PGProcess(self.pg_updater)
        self.pg_process.start()

        self.info = self.client.setup_session(self.config)  # Setup acconeer radar session
        self.num_points = self.info["data_length"]  # Length of data per sampel

        # Inputs for tracking
        self.f = self.config.sweep_rate
        self.dt = 1 / self.f
        self.number_of_averages = 2  # antalet medelvärdesbildningar
        self.number_of_time_samples = int(10 / self.dt) # number of time samples when plotting distance over time
        self.tracked_distance_over_time = np.zeros(self.number_of_time_samples) # array for distance over time
        self.average_com = []  # array med avstånd
        self.local_peaks_index = [] # index of local peaks
        self.track_peak_index = [] # index of last tracked peaks
        self.track_peaks_average_index = None # average of last tracked peaks
        self.threshold = None # threshold for removing small local peaks
        self.data_index = 0
        self.tracked_distance = None
        self.tracked_amplitude = None
        self.tracked_phase = None
        self.last_sweep = None # för plotten

        self.a = self.alpha(0.25, self.dt) # integration for last two values

        # acconeer graph
        self.lp_vel = 0
        self.hist_vel = np.zeros(self.number_of_time_samples)
        self.hist_pos = np.zeros(self.number_of_time_samples)

        # filter
        # global variable as input
        # coefficient vector
        self.coeff = [7.7519e-05, -2.1943e-19, -0.00017507, -0.0002844, -0.0001234, 0.00030536, 0.00066201, 0.0004875,
                 -0.00031655, -0.0011887, -0.0012209, 1.9897e-18, 0.0017329, 0.0023996, 0.00091246, -0.0020194,
                 -0.0039765, -0.0026926, 0.001624, 0.0057127, 0.0055361, -5.7122e-18, -0.007128, -0.0094788, -0.003479,
                 0.0074684, 0.014336, 0.0095102, -0.0056493, -0.019686, -0.019019, 9.8548e-18, 0.024919, 0.033935,
                 0.01293, -0.029337, -0.061027, -0.045529, 0.032296, 0.15036, 0.25711, 0.30003, 0.25711, 0.15036,
                 0.032296, -0.045529, -0.061027, -0.029337, 0.01293, 0.033935, 0.024919, 9.8548e-18, -0.019019,
                 -0.019686, -0.0056493, 0.0095102, 0.014336, 0.0074684, -0.003479, -0.0094788, -0.007128, -5.7122e-18,
                 0.0055361, 0.0057127, 0.001624, -0.0026926, -0.0039765, -0.0020194, 0.00091246, 0.0023996, 0.0017329,
                 1.9897e-18, -0.0012209, -0.0011887, -0.00031655, 0.0004875, 0.00066201, 0.00030536, -0.0001234,
                 -0.0002844, -0.00017507, -2.1943e-19, 7.7519e-05]
        self.N = len(self.coeff)  # Length of coefficient vector and length of input vector
        self.input_vector = np.zeros(self.N)  # the same length as coefficients. Important = zero from beginning
        self.output_vector_queue = queue.Queue()
        self.input_vector_index = 0  # for knowing where the latest input value is in input_vector

    def run(self):
        self.client.start_streaming()  # Starts Acconeers streaming server
        while self.go:
            # This data is an 1D array in terminal print, not in Python script however....
            data = self.get_data()
            tracked_data = self.tracking(data)
            filtered_tracked_data = self.filter(tracked_data["tracked phase"])
            print(filtered_tracked_data)
            self.output_vector_queue.put(filtered_tracked_data)  # put filtered data in output queue to send to SignalProcessing
            if tracked_data is not None:
                try:
                    self.pg_process.put_data(tracked_data)
                    # print("Tracked data: ", tracked_data["tracked distance"])
                except PGProccessDiedException:
                    break
            # if tracked_data is not None:
            #     print("Tracked data: ", tracked_data.get("tracked distance"))
        self.client.disconnect()

    def get_data(self):
        info, data = self.client.get_next()
        # print(data)
        # print("length of data {}".format(len(data[0])))
        # print("info {}".format(info))
        return data

    def tracking(self, data):
        # data = np.transpose(data)
        data = np.array(data).flatten()
        n = len(data)
        ampl = np.abs(data)
        power = ampl*ampl
        if np.sum(power) > 1e-6:

            max_peak_index = np.argmax(power)
            if self.data_index == 0: # first time
                self.track_peak_index.append(max_peak_index)
                self.track_peaks_average_index = max_peak_index
            else:
                self.local_peaks_index, _ = signal.find_peaks(power)  # find local maximas in data
                index = 0
                index_list = []
                for peak in self.local_peaks_index:
                    if np.abs(ampl[peak]) < self.threshold:
                        index_list.append(index)
                        index += 1
                np.delete(self.local_peaks_index, index_list)       # deletes all indexes with amplitude < threshold
                if len(self.local_peaks_index) == 0:
                    print("No local peak found")
                    self.track_peak_index.append(self.track_peak_index[-1])
                else:
                    peak_difference_index = np.subtract(self.local_peaks_index, self.track_peaks_average_index)
                    self.track_peak_index.append(self.local_peaks_index[np.argmin(np.abs(peak_difference_index))]) # min difference of index
                if len(self.track_peak_index) > self.number_of_averages:  # removes oldest value
                    self.track_peak_index.pop(0)
                if ampl[self.track_peak_index[-1]] < 0.5 * ampl[max_peak_index]:
                    self.track_peak_index.clear() # reset the array
                    self.track_peak_index.append(max_peak_index)  # new peak as global max
                self.track_peaks_average_index = int(np.round(self.a * (np.average(self.track_peak_index)) + (
                        1 - self.a) * self.track_peaks_average_index))

            # self.track_peaks_average_index = int(np.round(np.average(self.track_peak_index)))
            self.threshold = np.abs(ampl[self.track_peaks_average_index]) * 0.8 # threshold for next peak

            # com = np.argmax(power) / n  # globalt maximum #How does this work elementwise or not?
            # self.average_com.append(com)
            # if len(self.average_com) > self.averages:  # tar bort älsta värdet
            #     self.average_com.pop(0)
            # com = np.average(self.average_com)  # medelvärdet av tidigare avstånd
            com = self.track_peaks_average_index/len(data)

        else:
            com = 0

        if self.data_index == 0:
            self.lp_com = com
            self.tracked_data = None
            #self.data_index = 1
            self.lp_ampl = ampl
        else:
            self.lp_com = self.a*com + (1-self.a)*self.lp_com
            com_idx = int(self.lp_com * n)
            # Here begins our own code
            # First row is taken from acconeer plot for how to convert lp_com to m
            # Tracked amplitude is absolute value of data for the tracked index
            # Tracked phase is the angle between I and Q in data for tracked index
            self.tracked_distance = (1-self.lp_com) * \
                self.config.range_interval[0] + self.lp_com*self.config.range_interval[1]
            # print("Tracked Distance {} and com idx {}".format(self.com_x, com_idx))
            #self.tracked_amplitude = np.abs(data[com_idx])
            #self.tracked_phase = np.angle(data[com_idx])
            self.tracked_amplitude = np.abs(data[self.track_peaks_average_index])
            self.tracked_phase = np.angle(data[self.track_peaks_average_index])
            print(self.tracked_phase)

            # för plott
            self.lp_ampl = self.a * ampl + (1 - self.a) * self.lp_ampl

            tracked_distance = (1 - self.track_peaks_average_index/len(data)) * self.config.range_interval[0] + self.track_peaks_average_index/len(data) * self.config.range_interval[1]

            self.tracked_distance_over_time = np.roll(self.tracked_distance_over_time,-1)
            self.tracked_distance_over_time[-1] = tracked_distance# - np.mean(self.tracked_distance_over_time)

            delta_angle = np.angle(data[com_idx] * np.conj(self.last_sweep[com_idx]))
            vel = self.f * 2.5 * delta_angle / (2 * np.pi)
            self.lp_vel = self.a * vel + (1 - self.a) * self.lp_vel
            dp = self.lp_vel / self.f
            self.hist_pos = np.roll(self.hist_pos, -1)
            self.hist_pos[-1] = self.hist_pos[-2] + dp
            plot_hist_pos = self.hist_pos - self.hist_pos.mean()

            self.tracked_data = {"tracked distance": tracked_distance,
                                 "tracked amplitude": self.tracked_amplitude, "tracked phase": self.tracked_phase,
                                 "com": self.lp_com, "abs": self.lp_ampl, "tracked distance over time": plot_hist_pos,
                                 "tracked distance over time 2": self.tracked_distance_over_time}
        self.data_index +=1
        self.last_sweep = data
        return self.tracked_data

    def alpha(self, tau, dt):
        return 1 - np.exp(-dt/tau)

    # TODO Kolla på hur stor matrisen med tracking data blir. Ändras index efter ett tag

    def filter(self, input_value):  # send input value
        self.input_vector[self.input_vector_index] = input_value  # saves the input data in a vector continuously

        yn = 0  # to add all coefficients*values
        iterate_index = self.input_vector_index  # because variable value is changed in order to loop array
        for i in range(0, self.N - 1):  # iterate over all coefficients and relevant input values
            if iterate_index - i < 0:  # if iterate_index is negative begin from right hand side and work our way to the left
                iterate_index = self.N + i - 1  # moving to the rightmost location of array
            yn += self.coeff[i] * self.input_vector[iterate_index - i]  # add value of coefficient*data
        #self.output_vector_queue.put(yn)  # put filtered data in output queue to send to SignalProcessing

        self.input_vector_index += 1  # Note index += 1 before if statement
        if self.input_vector_index == self.N:  # len(input_vector = N)
            input_vector_index = 0
        return yn

# Test with acconeer plot is removed later on


class PGUpdater:
    def __init__(self, config):
        self.config = config
        self.interval = config.range_interval

    def setup(self, win):
        win.resize(1600, 1000)
        win.setWindowTitle("Track distance example")

        self.distance_plot = win.addPlot(row=0, col=0, colspan=2)
        self.distance_plot.showGrid(x=True, y=True)
        self.distance_plot.setLabel("left", "Amplitude")
        self.distance_plot.setLabel("bottom", "Depth (m)")
        self.distance_curve = self.distance_plot.plot(pen=example_utils.pg_pen_cycler(0))
        pen = example_utils.pg_pen_cycler(1)
        pen.setStyle(QtCore.Qt.DashLine)
        self.distance_inf_line = pg.InfiniteLine(pen=pen)
        self.distance_plot.addItem(self.distance_inf_line)

        # acconeers plot
        self.distance_over_time_plot = win.addPlot(row=1, col=0)
        self.distance_over_time_plot.showGrid(x=True, y=True)
        self.distance_over_time_plot.setLabel("left", "Distance")
        self.distance_over_time_plot.setLabel("bottom", "Time (s)")
        self.distance_over_time_curve = self.distance_over_time_plot.plot(pen=example_utils.pg_pen_cycler(0))
        self.distance_over_time_plot.setYRange(-8, 8)

        # our plot
        self.distance_over_time_plot2 = win.addPlot(row=1, col=1)
        self.distance_over_time_plot2.showGrid(x=True, y=True)
        self.distance_over_time_plot2.setLabel("left", "Distance")
        self.distance_over_time_plot2.setLabel("bottom", "Time (s)")
        self.distance_over_time_curve2 = self.distance_over_time_plot2.plot(pen=example_utils.pg_pen_cycler(0))
        self.distance_over_time_plot2.setYRange(0.4, 1.4)

        self.smooth_max = example_utils.SmoothMax(self.config.sweep_rate)
        self.first = True

    def update(self, data):
        if self.first:
            self.xs = np.linspace(*self.interval, len(data["abs"]))
            self.ts = np.linspace(-5, 0, len(data["tracked distance over time"]))
            # self.ts_zoom = np.linspace(-1.5, 0, len(data["hist_pos_zoom"]))
            self.first = False

        self.distance_curve.setData(self.xs, np.array(data["abs"]).flatten())
        self.distance_over_time_curve.setData(self.ts, data["tracked distance over time"])
        self.distance_over_time_curve2.setData(self.ts, data["tracked distance over time 2"])
        self.distance_plot.setYRange(0, self.smooth_max.update(np.amax(data["abs"])))
        self.distance_inf_line.setValue(data["tracked distance"])
