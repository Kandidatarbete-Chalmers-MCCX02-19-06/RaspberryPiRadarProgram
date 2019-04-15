import numpy as np
from scipy import signal  # Det här kanske behöver importeras på något annat sätt.
import matplotlib.pyplot as plt  # TODO: ta bort sen
import time  # TODO: Ta bort sen
from scipy.fftpack import fft
import threading
import queue


class SignalProcessing:

    def __init__(self, list_of_variables_for_threads):
        self.list_of_variables_for_threads = list_of_variables_for_threads
        self.go = list_of_variables_for_threads["go"]
        self.HR_filtered_queue = list_of_variables_for_threads["HR_filtered_queue"]
        self.HR_final_queue = list_of_variables_for_threads["HR_final_queue"]
        self.index_fft = 0
        self.sample_freq = list_of_variables_for_threads["sample_freq"]

        # Variables for Schmitt Trigger
        self.RR_filtered_queue = list_of_variables_for_threads["RR_filtered_queue"]
        self.RR_final_queue = list_of_variables_for_threads["RR_final_queue"]
        self.freqArrayTemp_last = []  # If no breathing rate is found use last value
        # print(list(self.RR_final_queue.queue))
        self.RTB_final_queue = list_of_variables_for_threads["RTB_final_queue"]

        # Starta heart_rate
        # self.heart_rate_thread = threading.Thread(target=self.heart_rate)
        # self.heart_rate_thread.start()
        # Starta schmitt
        self.schmittTrigger_thread = threading.Thread(target=self.schmittTrigger)
        self.schmittTrigger_thread.start()

    def heart_rate(self):
        T_resolution = 30
        overlap = 90
        beta = 1
        # Data in vector with length of window
        fft_window = np.zeros(T_resolution*self.sample_freq)
        i = 0
        while self.go:
            [freq, fft_signal_out] = self.windowedFFT(fft_window, overlap, beta)
        #     print(i) TODO: ta bort sen
        #     i += 1

        # plt.plot(freq, fft_signal_out)
        # plt.grid()
        # plt.show()

    ### windowedFFT ###
    # input:
    # fft_window: array to be filled with filtered data. And then to be fft:d
    # overlap: how many overlapping values between two consecutive fft windows. [in percentage]
    # beta: shape factor for kaiser window.
    # returns:
    # freq: corresponding frequency array
    # fft_signal_out: fft:d array
    def windowedFFT(self, fft_window, overlap, beta):
        window_width = len(fft_window)  # size of each window
        window_slide = int(np.round(window_width*(1-overlap/100)))  # number of overlapping points

        for i in range(window_slide):  # fills the fft_window array with window_slide values from filtered queue
            fft_window[self.index_fft] = self.HR_filtered_queue.get()
            self.index_fft += 1
            if self.index_fft == window_width-1:
                self.index_fft = 0

        # TODO: Check if necessary. # roll the matrix so that the last inserted value is to the right.
        fft_window = np.roll(fft_window, -(self.index_fft+1))
        [freq, fft_signal_out] = self.smartFFT(fft_window, beta)  # do fft
        # TODO: check if necessayr. # roll the matrix back
        fft_window = np.roll(fft_window, (self.index_fft+1))

        return freq, fft_signal_out

    ### smartFFT ###
    # input:
    # signal_in: in signal as an array
    # beta: shape factor for the window
    # returns:
    # freq: frequency array [Hz]
    # signal_out: fft of the in signal as an array

    def smartFFT(self, signal_in, beta):
        length_seq = len(signal_in)  # number of sequences
        window = np.kaiser(length_seq, beta)  # beta: shape factor
        signal_in = np.multiply(signal_in, window)

        signal_in_fft = fft(signal_in)  # two-sided fft of input signal

        signal_fft_abs = abs(signal_in_fft/length_seq)
        signal_out = 2*signal_fft_abs[0:length_seq//2]  # one-sided fft

        # frequency array corresponding to frequencies in the fft
        freq = self.sample_freq*np.arange(length_seq/2)/length_seq

        return freq, signal_out

    def schmittTrigger(self):
        # variable declaration
        Tc = 5  # medelvärdesbildning över antal [s]
        schNy = 0  # Schmitt ny
        schGa = 0  # Schmitt gammal
        Hcut = 0.001  # Higher hysteres cut. Change this according to filter. To manage startup of filter
        Lcut = -Hcut  # Lower hysteres cut
        # average over old values. TODO ev. ingen medelvärdesbildning. För att förhindra att andningen går mot ett fast värde. Vi vill se mer i realtid.
        avOver = 1
        freqArray = np.zeros(avOver)  # for averaging over old values
        count = 1  # for counting number of samples passed since last negative flank
        countHys = 1  # for counting if hysteresis should be updated
        FHighRR = 0.7  # To remove outliers in mean value
        FLowRR = 0.1  # To remove outliers in mean value
        # for saving respiratory_queue_RR old values for hysteresis
        trackedRRvector = np.zeros(self.sample_freq * Tc)  # to save old values

        while self.go:
            # to be able to use the same value in the whole loop
            trackedRRvector[countHys - 1] = self.RR_filtered_queue.get()
            #self.RTB_final_queue.put(trackedRRvector[countHys - 1])
            start = time.time()

            if countHys == self.sample_freq * Tc:
                Hcut = np.sqrt(np.mean(np.square(trackedRRvector)))  # rms of trackedRRvector
                Lcut = -Hcut
                print("Hcut: ", Hcut)       # se vad hysteres blir
                # TODO Hinder så att insvängningstiden för filtret hanteras
                countHys = 0

            # schNy = schGa   behövs inte. Görs nedan

            # trackedRRvector[countHys-1] is the current data from filter
            if trackedRRvector[countHys - 1] <= Lcut:
                schNy = 0
                if schGa == 1:
                    np.roll(freqArray, 1)
                    # save the new frequency between two negative flanks
                    freqArray[0] = self.sample_freq / count
                    # Take the mean value
                    # RR_final_queue is supposed to be the breathing rate queue that is sent to app
                    self.RR_final_queue.put(self.getMeanOfFreqArray(freqArray, FHighRR, FLowRR))
                    #print("Data added to schmitt should be sent to app")
                    #print("Breathing rate: ", self.RR_final_queue.get())
                    # TODO put getMeanOfFreqArray() into queue that connects to send bluetooth values instead
                    count = 0
            # trackedRRvector[countHys-1] is the current data from filter
            elif trackedRRvector[countHys - 1] >= Hcut:
                schNy = 1
                # TODO skicka data till app för realTime breathing

            schGa = schNy
            count += 1
            countHys += 1

            end = time.time()
            print("Tid genom schmittTrigger: ", end-start)

        print("out of schmittTrigger")

    # Used in schmittTrigger. Removes outliers and return mean value over last avOver values.
    def getMeanOfFreqArray(self, freqArray, FHighRR, FLowRR):  # remove all values > FHighRR and < FLowRR

        #freqArrayTemp = [x for x in freqArray if (x < FHighRR and x > FLowRR)]
        index_list = []
        index = 0
        #print("Before removal: Array {} \n Low and high hyst {},{}".format(freqArray, FLowRR, FHighRR))
        for freq_value in freqArray:
            if freq_value < FLowRR or freq_value > FHighRR or freq_value == 0:
                index_list.append(index)
            index += 1
        freqArrayTemp = np.delete(freqArray, index_list)
        #print("After removal but before deviation: ", freqArrayTemp)
        #freqArrayTemp = [x for x in freqArrayTemp if x != 0]
        # print(non_zero_temp)
        # print(type(non_zero_temp))
        #freqArrayTemp = freqArrayTemp[non_zero_temp]
        # a[nonzero(a)]

        median = np.median(freqArrayTemp)  # median value
        stanDev = np.std(freqArrayTemp)  # standard deviation

        # freqArrayTemp = [x for x in freqArrayTemp if (
        #    x > median - 3 * stanDev and x < median + 3 * stanDev)]
        # print(freqArrayTemp)
        index_list = []
        index = 0
        for freq_value in freqArrayTemp:
            if freq_value < median - 3 * stanDev and freq_value > median - 3 * stanDev:
                index_list.append(index)
            index += 1
        freqArrayTemp = np.delete(freqArrayTemp, index_list)
        #print("Last array before mean value {}".format(freqArrayTemp))
        # if len(freqArrayTemp) == 0:
        #     freqArrayTemp = self.freqArrayTemp_last
        # else:
        #     self.freqArrayTemp_last = freqArrayTemp
        mean = np.mean(freqArrayTemp)  # mean value of last avOver values excluding outliers
        # mean is nan if FreqArrayTemp is zero, which creates error when sending data to app
        if len(freqArrayTemp) == 0:
            mean = 0        # TODO ta det föregående värdet istället
            print("No values left in freqArrayTemp")
        mean = mean * 60  # To get resp rate in Hz to BPM
        mean = int(round(mean))
        #print("data from schmitt {}".format(mean))
        return mean


# MAIN ##  TODO: Ta bort MAIN sen


# #windowedFFT(data_in, sample_freq, T_resolution, overlap, beta)
# HR_filtered_queue = queue.Queue()
# HR_final_queue = queue.Queue()
# RR_filtered_queue = queue.Queue()
# RR_final_queue = queue.Queue()


# sample_freq = 20
# length_seq = 100000
# sample_spacing = 1/sample_freq

# t = np.arange(length_seq)*sample_spacing
# signal_in = 4*np.sin(1 * 2.0*np.pi*t) + 0*np.sin(2 * 2.0*np.pi*t)
# # print(signal_in)

# for i in range(len(signal_in)):
#     HR_filtered_queue.put(signal_in[i])
#     RR_filtered_queue.put(signal_in[i])

# go = ["True"]

# signal_processing = SignalProcessing(
#     go, HR_filtered_queue, HR_final_queue, RR_filtered_queue, RR_final_queue)

# time.sleep(0.5)
# go.pop(0)


#### Test av smartFFT ####
# sample_freq = 20
# length_seq = 600
# sample_spacing = 1/sample_freq

# t = np.arange(length_seq)*sample_spacing
# signal_in = 4*np.sin(1 * 2.0*np.pi*t) + 0.5*np.sin(4 * 2.0*np.pi*t)
# #signal_in = np.roll(signal_in, 5)
# beta = 1

# [freq,signal_out] = smartFFT(signal_in,sample_freq,beta)

# plt.plot(freq, signal_out)
# plt.grid()
# plt.show()
