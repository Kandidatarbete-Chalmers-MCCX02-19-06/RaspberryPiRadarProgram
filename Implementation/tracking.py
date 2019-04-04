import queue
import numpy as np
import scipy as sp
import matplotlib.pyplot as plt


# data is stored in self.data
def tracking(self):
    counter = 0  # Used only for if statement only for first iteration and not when data_idx goes back to zero
    N_avg = 10  # Number of total peaks to average over
    self.start_distance = 0.37  # Initial guess for where
    self.data_matrix[self.data_idx][:] = self.data
    dist = self.num_points     # number of datapoints in data # self.num_points
    # maximum value
    interval = self.config.range_interval[1] - self.config.range_interval[0]

    if self.data_idx == 0 and counter == 0:      # things that only happens first time
        # chooses index closest to starting distance
        I = np.round(
            ((self.start_distance - self.config.range_interval[0]) / interval) * dist)

        #I = np.abs(self.data).index(sp.signal.find_peaks(np.abs(self.data)))

        self.I_peaks[0] = I
        self.locks = sp.signal.find_peaks(np.abs(self.data))
        I = np.amin(np.abs(self.locks - self.I_peaks[0]))
        self.I_peaks[0] = self.locks[I]
        self.I_peaks_filtered[0] = self.I_peaks[0]
        self.tracked_distance[0] = self.I_peaks_filtered[0] / dist * interval
        self.tracked_amplitude[0] = np.abs(self.data(self.I_peaks_filtered[0]))
        self.tracked_phase[0] = np.angle(self.data(self.I_peaks_filtered[0]))

    # After first seq continous tracking
    else:
        self.locks = None
        self.locks = sp.signal.find_peaks(np.abs(self.data))
        I = np.amin(self.locks - self.I_peaks_filtered[self.data_idx - 1])
        if self.locks == None:
            self.I_peaks[self.data_idx] = self.I_peaks[self.data_idx-1]
        else:
            self.I_peaks[self.data_idx] = self.locks[I]
        if counter == 0:
            self.i_avg_start = np.amax([1, self.data_idx - N_avg])
        else:
            self.i_avg_start = self.data_idx - N_avg
            counter = 1

        self.I_peaks_filtered[self.data_idx] = np.round(np.mean(self.I_peaks(self.i_avg_start: self.data_idx))) #TODO:Syntaxfel
        self.tracked_distance[self.data_idx] = self.I_peaks_filtered[self.data_idx] / dist * interval

        self.tracked_amplitude[self.data_idx] = np.abs(
            self.data(self.I_peaks_filtered[self.data_idx]))
        self.data(self.I_peaks_filtered[self.data_idx]) #TODO:Den här raden gör ingenting...?!
        self.tracked_phase[self.data_idx] = np.angle(
            self.data(self.I_peaks_filtered[self.data_idx]))

        plt.figure(1)
        plt.plot(self.tracked_distance)
        plt.title('Tracked distance')

        plt.figure(2)
        plt.plot(self.tracked_phase)
        plt.title('Tracked phase')

        plt.figure(3)
        plt.plot(self.tracked_amplitude)
        plt.title('Tracked amplitude')
