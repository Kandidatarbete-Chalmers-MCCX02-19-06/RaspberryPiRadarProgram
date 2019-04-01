import queue
import numpy as np
import scipy as sp


# data is stored in self.data
def tracking(self):
    self.data_matrix[self.data_idx][:] = self.data
    dist = self.num_points     # number of datapoints in data # self.num_points
    interval = self.config.range_interval[1] - self.config.range_interval[0]       # maximum value
    self.start_distance = 0.37
    # choosen index closest to starting distance
    I = round(((self.start_distance - self.config.range_interval[0]) / interval) * dist)

    if self.data_idx == 0:      # things that only happens first time
        self.I_peaks[0] = I
        self.locks = sp.signal.find_peaks(np.abs(self.data))
        self.I_peaks[0] = np.amin(np.abs(self.locks - self.I_peaks[0]))  # Maybe one more Locs
        self.I_peaks_filtered[0] = self.I_peaks[0]
        self.tracked_distance = self.I_peaks_filtered[0] / dist * interval
        self.tracked_amplitude = np.abs(self.data(self.I_peaks_filtered[0]))
        self.tracked_phase = np.angle(self.data(self.I_peaks_filtered[0]))

     # After first seq continous tracking
     elif:
        self.locks = None     
        self.locks = sp.signal.find_peaks(np.abs(self.data))
        I = np.amin(self.locks - self.I_peaks_filtered[self.data_idx -1])
        if self.locks == None:
                self.I_peaks[self.data_idx] = self.I_peaks[self.data_idx-1]
        self.I_peaks[self.data_idx] = 



     
