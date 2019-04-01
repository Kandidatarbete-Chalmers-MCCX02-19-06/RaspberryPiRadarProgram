import queue
import numpy as np
import scipy as sp


# data is stored in self.data
def tracking():
    self.data_matrix[self.data_idx][:] = self.data
    dist = len(self.data)       # number of datapoints in data
    interval = self.config.range_interval[1] - self.config.range_interval[0]       # maximum value
    self.start_distance = 0.37
    I = round(((self.start_distance - self.config.range_interval[0]) / interval) * dist)        # choosen index closest to starting distance

    if self.data_idx == 0:      # things that only happens first time
        self.I_peak[self.data_idx] = I

