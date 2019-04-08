import time
import threading
import numpy as np
from scipy import signal
import queue
import copy       # import for static variable run in class

from acconeer_utils.clients.reg.client import RegClient
from acconeer_utils.clients.json.client import JSONClient
from acconeer_utils.clients import configs
from acconeer_utils import example_utils
from acconeer_utils.mpl_process import PlotProcess, PlotProccessDiedException, FigureUpdater


class DataAcquisition(threading.Thread):
    def __init__(self, go):
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
        self.config.range_interval = [0.2, 0.6]  # Measurement interval
        self.config.sweep_rate = 20  # Frequency for collecting data
        self.config.gain = 1  # Gain between 0 and 1.

        self.info = self.client.setup_session(self.config)  # Setup acconeer radar session
        self.num_points = self.info["data_length"]  # Length of data per sampel

        super(DataAcquisition, self).__init__()  # Inherit threading vitals

    def run(self):
        self.client.start_streaming()  # Starts Acconeers streaming server
        i = 0
        while self.go:
            data = self.get_data()
            print("Data is working:", i)
            i += 1

        self.client.disconnect()

    def get_data(self):
        info, data = self.client.get_next()
        return data
