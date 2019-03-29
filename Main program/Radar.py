import time
import threading
import numpy as np
import queue
import copy

from acconeer_utils.clients.reg.client import RegClient
from acconeer_utils.clients.json.client import JSONClient
from acconeer_utils.clients import configs
from acconeer_utils import example_utils
from acconeer_utils.mpl_process import PlotProcess, PlotProccessDiedException, FigureUpdater


class Radar(threading.Thread):
    def __init__(self, HR_filter_queue, interrupt_queue):  # Lägg till RR_filter_queue som inputargument
        # Setup for collecting data from radar
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

        self.config.range_interval = [0.2, 0.6]  # Measurement interval
        self.config.sweep_rate = 100  # Frequency for collecting data
        self.config.gain = 1  # Gain between 0 and 1.
        self.time = 1  # Duration for a set amount of sequences
        self.seq = self.config.sweep_rate * self.time

        self.info = self.client.setup_session(self.config)  # Setup acconeer radar session
        self.num_points = self.info["data_length"]  # Amount of data points per sampel

        # Vector for radar values from tracked data
        self.peak_vector = np.zeros((1, self.seq), dtype=np.csingle)
        self.data_idx = 0  # Inedex for peak vector used for filtering

        self.HR_filter_queue = HR_filter_queue
        #self.RR_filter_queue = RR_filter_queue
        self.interrupt_queue = interrupt_queue
        super(Radar, self).__init__()  # Inherit threading vitals

    # Loop which collects data from the radar, tracks the maximum peak and filters it for further signal processing. The final filtered data is put into a queue.
    def run(self):
        self.client.start_streaming()  # Starts Acconeers streaming server
        while self.interrupt_queue.empty():
            # for i in range(self.seq*2):
            self.get_data()
            self.tracker()
            self.filter_HeartRate()
            self.filter_RespRate()
            self.data_idx += 1
            if self.data_idx == self.config.sweep_rate:
                print("Still getting data")
                self.HR_filter_queue.put(2)
            if self.data_idx >= self.seq:  # Resets matrix index to zero for filtering.
                self.data_idx = 0

        self.client.disconnect()

    # Method to collect data from the streaming server
    def get_data(self):
        self.info, self.data = self.client.get_next()

    # Filter for heart rate using the last X sampels according to data_idx. Saves data to queue
    def filter_HeartRate(self):
        HR_peak_vector = copy.copy(self.peak_vector)
        for i in range(5):
            HR_peak_vector[0][i] = 0
        # self.HR_filter_queue.put(HR_peak_vector)

    # Filter for Respitory rate. Saves data to queue

    def filter_RespRate(self):
        # RR_peak_vector = copy.copy(self.peak_vector)
        # for i in range(5):
        #     RR_peak_vector[0][i] = 0
        # self.RR_filter_queue.put(RR_peak_vector)
        pass

    # Tracks the maximum peak from collected data which is filtered for further signal processing
    def tracker(self):
        self.amplitude = np.abs(self.data)
        self.peak = np.argmax(self.amplitude)
        self.peak_vector[0][self.data_idx] = self.data[0][self.peak]
