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


class Radar():
    def __init__(self, radar_queue, interrupt_queue):
        # Setup for collecting data from radar
        self.args = example_utils.ExampleArgumentParser().parse_args()
        example_utils.config_logging(self.args)
        if self.args.socket_addr:
            self.client = JSONClient(self.args.socket_addr)
        else:
            port = self.args.serial_port or example_utils.autodetect_serial_port()
            self.client = RegClient(port)

        self.client.squeeze = False
        self.config = configs.IQServiceConfig()
        self.config.sensor = self.args.sensors

        self.config.range_interval = [0.2, 0.6]  # Measurement interval
        self.config.sweep_rate = 1  # Frequency for collecting data
        self.config.gain = 1  # Gain between 0 and 1.
        self.time = 10  # Duration for a set amount of sequences
        self.seq = self.config.sweep_rate * self.time

        self.info = self.client.setup_session(self.config)  # Setup acconeer radar session
        self.num_points = self.info["data_length"]  # Amount of data points per sampel

        # Vector for radar values from tracked data
        self.peak_vector = np.zeros((1, self.seq), dtype=np.csingle)
        self.data_idx = 0  # Inedex for peak vector used for filtering

        self.radar_queue = radar_queue
        self.interrupt_queue = interrupt_queue
        self.timeout = time.time() + self.time

    # Loop which collects data from the radar, tracks the maximum peak and filters it for further signal processing. The final filtered data is put into a queue.
    def get_data(self):
        self.client.start_streaming()  # Starts Acconeers streaming server
        while True:
            self.info, self.data = self.client.get_next()
            print("Getting data")
            if self.interrupt_queue.empty() == False or time.time() >= self.timeout:  # Interrupt from bluetooth
                # self.interrupt_queue.get()
                print('Breaking loop')
                break
        self.client.disconnect()
