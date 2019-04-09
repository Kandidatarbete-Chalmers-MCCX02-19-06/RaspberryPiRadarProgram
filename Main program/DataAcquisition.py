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
        self.config.sweep_rate = 80  # Frequency for collecting data
        self.config.gain = 0.9  # Gain between 0 and 1.

        # self.sweep_index = 0 # för plotten
        # för plotten
        self.pg_updater = PGUpdater(self.config)
        self.pg_process = PGProcess(self.pg_updater)
        self.pg_process.start()

        self.info = self.client.setup_session(self.config)  # Setup acconeer radar session
        self.num_points = self.info["data_length"]  # Length of data per sampel

        # Inputs for tracking
        self.f = self.config.sweep_rate
        self.dt = 1 / self.f
        self.number_of_averages = 3  # antalet medelvärdesbildningar
        self.average_com = []  # array med avstånd
        self.local_peaks_index = [] # index of local peaks
        self.track_peak_index = [] # index of last tracked peaks
        self.local_peaks_average_index = None # average of last tracked peaks
        self.threshold = None # threshold for removing small local peaks
        self.data_index = 0
        # self.real_dist = np.linspace(
        #    self.config.range_interval[0], self.config.range_interval[1], num=self.num_points)
        self.tracked_distance = None
        self.tracked_amplitude = None
        self.tracked_phase = None
        self.last_sweep = None # för plotten

    def run(self):
        self.client.start_streaming()  # Starts Acconeers streaming server
        while self.go:
            # This data is an 1D array in terminal print, not in Python script however....
            data = self.get_data()
            tracked_data = self.tracking(data)
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
        data = np.transpose(data)
        data = np.array(data).flatten()
        n = len(data)
        ampl = np.abs(data)
        power = ampl*ampl
        if np.sum(power) > 1e-6:

            max_peak = np.argmax(power)
            if self.data_index: # first time
                self.local_peaks_index.append(max_peak)
                self.threshold = 0.5 * max_peak
            else:
                self.local_peaks_index, _ = signal.find_peaks(np.abs(data))  # find local maximas in data TODO improve to linear algebra
                # self.local_peaks_index = np.array(self.local_peaks_index).flatten()
                index = 0
                print(self.threshold)
                for peak in self.local_peaks_index:
                    if np.abs(data[peak]) < self.threshold:
                        np.delete(self.local_peaks_index, index)
                        index += 1
                #self.local_peaks_index = self.local_peaks_index[(np.abs(data[:]) > self.threshold)]
                # self.local_peaks_index = [x for x in self.local_peaks_index if (np.abs(data[x]) > self.threshold)]
                peak_difference_index = np.subtract(self.local_peaks_index, self.local_peaks_average_index)
                self.track_peak_index.append(np.argmin(np.abs(peak_difference_index))) # min difference of index
                if len(self.local_peaks_index) == 0:
                    print("No local peak found")
                    self.track_peak_index[-1] = self.track_peak_index[-2]
                if len(self.track_peak_index) > self.number_of_averages:  # removes oldest value
                    self.track_peak_index.pop(0)
                if self.track_peak_index[-1] < 0.1 * max_peak:
                    self.local_peaks_index.clear()  # reset the array
                    self.local_peaks_index.append(max_peak)  # new peak as global max
                    # self.local_peaks_index[:] = max_peak # reset the array and take the new global max as
                    self.threshold = 0.5 * max_peak

            self.local_peaks_avarage_index = np.round(np.average(self.track_peak_index))
            print(type(self.local_peaks_avarage_index))
            self.threshold = np.abs(data[self.local_peaks_average_index]) * 0.5 # threshold for

            # com = np.argmax(power) / n  # globalt maximum #How does this work elementwise or not?
            # self.average_com.append(com)
            # if len(self.average_com) > self.averages:  # tar bort älsta värdet
            #     self.average_com.pop(0)
            # com = np.average(self.average_com)  # medelvärdet av tidigare avstånd
            com = self.local_peaks_avarage_index/len(data)

        else:
            com = 0

        if self.data_index == 0:
            self.lp_com = com
            self.tracked_data = None
            self.data_index = 1
            self.lp_ampl = ampl
        else:
            # a = self.alpha(0.1, self.dt)
            # self.lp_ampl = a * ampl + (1 - a) * self.lp_ampl
            # a = self.alpha(0.25, self.dt)
            # self.lp_com = a * com + (1 - a) * self.lp_com
            #
            # com_idx = int(self.lp_com * n)
            # delta_angle = np.angle(data[com_idx] * np.conj(self.last_sweep[com_idx]))
            # vel = self.f * 2.5 * delta_angle / (2 * np.pi)
            #
            # a = self.alpha(0.1, self.dt)
            # self.lp_vel = a * vel + (1 - a) * self.lp_vel
            #
            # self.hist_vel = np.roll(self.hist_vel, -1)
            # self.hist_vel[-1] = self.lp_vel
            #
            # dp = self.lp_vel / self.f
            # self.hist_pos = np.roll(self.hist_pos, -1)
            # self.hist_pos[-1] = self.hist_pos[-2] + dp
            #
            # hist_len = len(self.hist_pos)
            # plot_hist_pos = self.hist_pos - self.hist_pos.mean()
            # plot_hist_pos_zoom = self.hist_pos[hist_len // 2:] - self.hist_pos[hist_len // 2:].mean()
            #
            # iq_val = np.exp(1j * np.angle(data[com_idx])) * self.lp_ampl[com_idx]
            #
            # plot_data = {
            #     "abs": self.lp_ampl,
            #     "arg": np.angle(data),
            #     "com": self.lp_com,
            #     "hist_pos": plot_hist_pos,
            #     "hist_pos_zoom": plot_hist_pos_zoom,
            #     "iq_val": iq_val,
            # }
            #
            # self.last_sweep = data
            # self.data_index += 1
            ################ ################ egen kod nedan ################# ###############
            a = self.alpha(0.25, self.dt)
            self.lp_com = a*com + (1-a)*self.lp_com
            com_idx = int(self.lp_com * n)
            # Here begins our own code
            # First row is taken from acconeer plot for how to convert lp_com to m
            # Tracked amplitude is absolute value of data for the tracked index
            # Tracked phase is the angle between I and Q in data for tracked index
            self.tracked_distance = (1-self.lp_com) * \
                self.config.range_interval[0] + self.lp_com*self.config.range_interval[1]
            # print("Tracked Distance {} and com idx {}".format(self.com_x, com_idx))
            self.tracked_amplitude = np.abs(data[com_idx])
            self.tracked_phase = np.angle(data[com_idx])

            # för plott
            self.lp_ampl = a * ampl + (1 - a) * self.lp_ampl

            tracked_distance = (1 - self.local_peaks_avarage_index/len(data)) * self.config.range_interval[0] + self.local_peaks_avarage_index/len(data) * self.config.range_interval[1]

            # self.tracked_data = {"tracked distance": self.tracked_distance,
            #                      "tracked amplitude": self.tracked_amplitude, "tracked phase": self.tracked_phase, "com": self.lp_com, "abs": self.lp_ampl}

            self.tracked_data = {"tracked distance": tracked_distance,
                                 "tracked amplitude": self.tracked_amplitude, "tracked phase": self.tracked_phase,
                                 "com": self.lp_com, "abs": self.lp_ampl}

        return self.tracked_data

    def alpha(self, tau, dt):
        return 1 - np.exp(-dt/tau)

# Test with acconeer plot is removed later on


class PGUpdater:
    def __init__(self, config):
        self.config = config
        self.interval = config.range_interval

    def setup(self, win):
        win.resize(800, 600)
        win.setWindowTitle("Albins tracking example")

        self.distance_plot = win.addPlot(row=0, col=0)
        self.distance_plot.showGrid(x=True, y=True)
        self.distance_plot.setLabel("left", "Amplitude")
        self.distance_plot.setLabel("bottom", "Depth (m)")
        self.distance_curve = self.distance_plot.plot(pen=example_utils.pg_pen_cycler(0))
        pen = example_utils.pg_pen_cycler(1)
        pen.setStyle(QtCore.Qt.DashLine)
        self.distance_inf_line = pg.InfiniteLine(pen=pen)
        self.distance_plot.addItem(self.distance_inf_line)

        # self.abs_plot = win.addPlot(row=0, col=0)
        # self.abs_plot.showGrid(x=True, y=True)
        # self.abs_plot.setLabel("left", "Amplitude")
        # self.abs_plot.setLabel("bottom", "Depth (m)")
        # self.abs_curve = self.abs_plot.plot(pen=example_utils.pg_pen_cycler(0))
        # pen = example_utils.pg_pen_cycler(1)
        # pen.setStyle(QtCore.Qt.DashLine)
        # self.abs_inf_line = pg.InfiniteLine(pen=pen)
        # self.abs_plot.addItem(self.abs_inf_line)

        # self.arg_plot = win.addPlot(row=1, col=0)
        # self.arg_plot.showGrid(x=True, y=True)
        # self.arg_plot.setLabel("bottom", "Depth (m)")
        # self.arg_plot.setLabel("left", "Phase")
        # self.arg_plot.setYRange(-np.pi, np.pi)
        # self.arg_plot.getAxis("left").setTicks(example_utils.pg_phase_ticks)
        # self.arg_curve = self.arg_plot.plot(pen=example_utils.pg_pen_cycler(0))
        # self.arg_inf_line = pg.InfiniteLine(pen=pen)
        # self.arg_plot.addItem(self.arg_inf_line)
        #
        # self.iq_plot = win.addPlot(row=1, col=1, title="IQ at line")
        # example_utils.pg_setup_polar_plot(self.iq_plot, 0.5)
        # self.iq_curve = self.iq_plot.plot(pen=example_utils.pg_pen_cycler())
        # self.iq_scatter = pg.ScatterPlotItem(
        #     brush=pg.mkBrush(example_utils.color_cycler()),
        #     size=15,
        # )
        # self.iq_plot.addItem(self.iq_scatter)
        #
        # self.hist_plot = win.addPlot(row=0, col=1, colspan=2)
        # self.hist_plot.showGrid(x=True, y=True)
        # self.hist_plot.setLabel("bottom", "Time (s)")
        # self.hist_plot.setLabel("left", "Tracking (mm)")
        # self.hist_curve = self.hist_plot.plot(pen=example_utils.pg_pen_cycler())
        # self.hist_plot.setYRange(-5, 5)
        #
        # self.hist_zoom_plot = win.addPlot(row=1, col=2)
        # self.hist_zoom_plot.showGrid(x=True, y=True)
        # self.hist_zoom_plot.setLabel("bottom", "Time (s)")
        # self.hist_zoom_plot.setLabel("left", "Tracking (mm)")
        # self.hist_zoom_curve = self.hist_zoom_plot.plot(pen=example_utils.pg_pen_cycler())
        # self.hist_zoom_plot.setYRange(-0.5, 0.5)

        self.smooth_max = example_utils.SmoothMax(self.config.sweep_rate)
        self.first = True

    def update(self, data):
        if self.first:
            self.xs = np.linspace(*self.interval, len(data["abs"]))
            # self.ts = np.linspace(-3, 0, len(data["hist_pos"]))
            # self.ts_zoom = np.linspace(-1.5, 0, len(data["hist_pos_zoom"]))
            self.first = False

        # com_x = (1-data["com"])*self.interval[0] + data["com"]*self.interval[1]

        self.distance_curve.setData(self.xs, np.array(data["abs"]).flatten())
        self.distance_plot.setYRange(0, self.smooth_max.update(np.amax(data["abs"])))
        self.distance_inf_line.setValue(data["tracked distance"])
        # self.arg_curve.setData(self.xs, data["arg"])
        # self.arg_inf_line.setValue(com_x)
        # self.hist_curve.setData(self.ts, data["hist_pos"])
        # self.hist_zoom_curve.setData(self.ts_zoom, data["hist_pos_zoom"])
        # self.iq_curve.setData([0, np.real(data["iq_val"])], [0, np.imag(data["iq_val"])])
        # self.iq_scatter.setData([np.real(data["iq_val"])], [np.imag(data["iq_val"])])
