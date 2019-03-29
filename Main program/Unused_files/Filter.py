import time
import threading
import numpy as np
import queue
import copy


class Filter(threading.Thread):
    def __init__(self, radar_queue, interrupt_queue):
        # Setup for collecting data from radar

        self.peak_vector_length = 5
        b = 0

        # Vector for radar values from tracked data #Hur lång ska den vara?
        self.peak_vector = np.zeros((1, self.peak_vector_length), dtype=np.csingle)
        self.data_idx = 0  # Inedex for peak vector used for filtering

        self.radar_queue = radar_queue
        self.interrupt_queue = interrupt_queue
        super(Filter, self).__init__()  # Inherit threading vitals

    # Loop which collects data from the radar, tracks the maximum peak and filters it for further signal processing. The final filtered data is put into a queue.
    def run(self):
        while True:
            # for i in range(self.seq*2):
            self.tracker()
            self.filter_HeartRate()
            self.filter_RespRate()
            self.data_idx += 1
            if self.data_idx >= self.peak_vector_length:  # Resets matrix index to zero for filtering.
                self.data_idx = 0
            if self.interrupt_queue.empty() == False:  # Interrupt from main
                print('Breaking loop')
                break

    # Filter for heart rate using the last X sampels according to data_idx. Saves data to queue
    def filter_HeartRate(self):
        HR_peak_vector = copy.copy(self.peak_vector)
        for i in range(5):
            HR_peak_vector[0][i] = 0
        print(HR_peak_vector)
        self.radar_queue.put(HR_peak_vector)

    # Filter for Respitory rate. Saves data to queue

    def filter_RespRate(self):
        pass

    # Tracks the maximum peak from collected data which is filtered for further signal processing
    def tracker(self):
        self.amplitude = np.abs(self.data)
        self.peak = np.argmax(self.amplitude)
        self.peak_vector[0][self.data_idx] = self.data[0][self.peak]
