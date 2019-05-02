import numpy as np
from scipy import signal  # Det här kanske behöver importeras på något annat sätt.
import matplotlib.pyplot as plt  # TODO: ta bort sen
import time  # TODO: Ta bort sen
from scipy.fftpack import fft
from scipy.signal import spectrogram  # To plot spectrogram of FFT.
import threading
import queue


class SignalProcessing:

    # FFTfreq and FFTamplitude are temporary for testing FFT. Remove later
    def __init__(self, list_of_variables_for_threads, bluetooth_server, FFTfreq, FFTamplitude):
        self.list_of_variables_for_threads = list_of_variables_for_threads
        self.go = list_of_variables_for_threads["go"]
        self.HR_filtered_queue = list_of_variables_for_threads["HR_filtered_queue"]
        self.HR_final_queue = list_of_variables_for_threads["HR_final_queue"]       # TODO ta bort
        self.sample_freq = list_of_variables_for_threads["sample_freq"]
        self.bluetooth_server = bluetooth_server

        # Variables for Schmitt Trigger
        self.RR_filtered_queue = list_of_variables_for_threads["RR_filtered_queue"]
        self.RR_final_queue = list_of_variables_for_threads["RR_final_queue"]
        self.freqArrayTemp_last = []  # If no breathing rate is found use last value
        # print(list(self.RR_final_queue.queue))
        self.RTB_final_queue = list_of_variables_for_threads["RTB_final_queue"]
        self.time_when_sent_last_value = None  # to check time passed after sent a value

        # Variables for Pulse detection
        self.index_fft = 0
        self.T_resolution = 15  # förut 30
        self.overlap = 90  # Percentage of old values for the new FFT
        self.beta = 1  # Kaiser window form
        self.tau = 12  # TODO Beskriva alla variabler
        # Data in vector with length of window
        self.fft_window = np.zeros(self.T_resolution*self.sample_freq)  # Width in samples of FFT
        self.length_fft_window = len(self.fft_window)  # length of fft_window array
        self.window_width = int(len(self.fft_window))
        # window_width_half = int(window_width/2)  # Since FFT only processes half of freq (Nyqvist)
        self.window_slide = int(np.round(self.window_width*(1-self.overlap/100)))
        self.freq = self.sample_freq * \
            np.arange(self.length_fft_window/2)/self.length_fft_window  # Evenly spaced freq array

        self.delta_T = self.window_slide / self.sample_freq
        # int(round(self.tau / self.delta_T))  # Make tau is larger than delta_T, else it will be zero and programme will fail.
        self.number_of_old_FFT = 10
        self.FFT_old_values = np.zeros((self.number_of_old_FFT, int(
            self.window_width/2)))  # Saving old values for moving mean
        # Starta heart_rate
        self.heart_rate_thread = threading.Thread(target=self.heart_rate)
        self.heart_rate_thread.start()
        print("Start thread heart_rate")
        # Starta schmitt
        self.schmittTrigger_thread = threading.Thread(target=self.schmittTrigger)
        self.schmittTrigger_thread.start()

        self.last_time = time.time()
        self.time = time.time()

        # Temporary for test of FFT
        self.FFTfreq = FFTfreq
        self.FFTamplitude = FFTamplitude
        self.peak_freq = []
        self.peak_amplitude = []
        self.peak_weighted = []
        self.len_fft = 0

    # Kaos i koden, behöver struktureras upp och alla konstanter måste defineras i början
    # Följer just nu Matlab strukturen.

    def heart_rate(self):  # MAIN for finding pulse
        # print("heart_rate thread started")
        index_in_FFT_old_values = 0  # Placement of old FFT in FFT_old_values
        FFT_counter = 1  # In start to avg over FFT_counter before FFT_old_values is filled to max
        found_heart_freq_old = 180/60  # Guess the first freq
        found_heart_freq_amplitude_old = -20
        # Variables for weigthed peaks
        #multiplication_factor = 20
        time_constant = 2
        start_time = time.time()
        first_real_value = True  # the first real heart rate found
        old_heart_freq_list = []

        while self.go:
            # print("in while loop heart_rate")
            fft_signal_out = self.windowedFFT()
            fft_signal_out_dB = 20*np.log10(fft_signal_out)
            self.FFT_old_values[index_in_FFT_old_values][:] = fft_signal_out_dB

            # RBW = self.freq[1] - self.freq[0] # Used where?
            #print("This new FFT: ", fft_signal_out_dB[2])
            saved_old = self.FFT_old_values[:, 2]
            #print("length: ", len(saved_old))
            #print("Saved old FFT: ", saved_old)
            #print("Rows", len(self.FFT_old_values))
            #print("Columns", len(self.FFT_old_values[0]))
            # fft movemean
            FFT_averaged = self.mean_of_old_values(FFT_counter)
            #print("Averaged FFT: ", FFT_averaged[2])
            # Returns the peaks in set inteval from averaged FFT
            peak_freq, peak_amplitude = self.findPeaks(FFT_averaged)
            #print('length of peak_freq',len(peak_freq))
            #print('length of peak_amplitude', len(peak_amplitude))
            if len(peak_freq) > 0 and np.amax(peak_amplitude) > -30 and time.time() - start_time > 50:
                # In case zero peaks, use last value, and to not trigger on noise, and there is just noise before 30 seconds has passed
                # Going into own method when tested and working staying in "main loop"
                delta_freq = []
                for freq in peak_freq:
                    delta_freq.append(freq - found_heart_freq_old)
                #self.peak_weighted = np.add(
                #    peak_amplitude, multiplication_factor*np.exp(-np.abs(delta_freq)/time_constant))
                self.peak_weighted = []
                close_peaks_index = []
                close_peaks = []
                try:
                    for i in range(0,len(peak_freq)):  # Weight the peaks found depending on their amplitude,
                        if peak_freq[i] < 1:
                            multiplication_factor = 7 # to lower the noise peak under 1 Hz
                        else:
                            multiplication_factor = 10
                        # distance to the last tracked peak, and on the frequency (the noise is kind of 1/f, so to to fix that multiply with f)
                        self.peak_weighted.append(peak_amplitude[i]+multiplication_factor*np.exp(-np.abs(peak_freq[i]-found_heart_freq_old)/time_constant)*np.sqrt(np.sqrt(peak_freq[i])))
                        #print('freq diff',np.abs(peak_freq[i] - found_heart_freq_old))
                        #print('amp diff',np.abs(peak_amplitude[i] - found_heart_freq_amplitude_old))
                        #print('old amp',found_heart_freq_amplitude_old)
                        if np.abs(peak_freq[i] - found_heart_freq_old) < 0.3 and np.abs(peak_amplitude[i] - found_heart_freq_amplitude_old) < 5:# and (found_heart_freq_old < 1 or peak_freq[i] > 1):
                            close_peaks_index.append(i)
                            close_peaks.append(peak_freq[i])

                    found_heart_freq = peak_freq[np.argmax(np.array(self.peak_weighted))]
                    found_heart_freq_amplitude_old = self.peak_amplitude[np.argmax(np.array(self.peak_weighted))]

                    if len(close_peaks_index) > 2:
                        print('averaging, old:',found_heart_freq,close_peaks_index)
                        #found_heart_freq = np.mean(peak_freq[i] for i in close_peaks_index)
                        found_heart_freq = np.mean(close_peaks)
                except Exception as e:
                    print('exept in heart peak',e)
                    found_heart_freq = 0

                if first_real_value and found_heart_freq > 1:
                    first_real_value = False
                if found_heart_freq < 1 and first_real_value:  # Do not trigger on the large noise peak under 1 Hz
                    found_heart_freq = 0


                found_heart_freq_old = found_heart_freq
            elif len(peak_freq) > 0:
                found_heart_freq = found_heart_freq_old  # just use the last values
            else:
                # Just noise
                #found_heart_freq = found_heart_freq_old
                found_heart_freq = 0
                self.peak_weighted.clear()


            if not first_real_value:
                print("Found heart rate Hz and BPM: ", found_heart_freq, int(60*found_heart_freq))
                found_heart_rate = int(60 * found_heart_freq)  # Send to app
                self.bluetooth_server.write_data_to_app(found_heart_rate, 'heart rate')
            else:
                print("Waiting to find heart rate")
                found_heart_rate = 0  # Send to app
                self.bluetooth_server.write_data_to_app(found_heart_rate, 'heart rate')
            # BPM_search = self.freq * 60 # Used where?
            # print("past plot heart rate")

            # increment counters in loop
            if FFT_counter < self.number_of_old_FFT:
                FFT_counter += 1
            index_in_FFT_old_values += 1
            if index_in_FFT_old_values == self.number_of_old_FFT:
                index_in_FFT_old_values = 0

    def mean_of_old_values(self, FFT_counter):  # Check
        FFT_average_over = np.zeros(int(self.window_width/2))
        for columns in range(0, int(self.window_width/2)):
            for rows in range(0, self.number_of_old_FFT):
                FFT_average_over[columns] = self.FFT_old_values[rows][columns] + \
                    FFT_average_over[columns]
        #print("Mean of old values: ", self.FFT_average_out / FFT_counter)
        return FFT_average_over / FFT_counter

    ### windowedFFT ###
    # input:
    # fft_window: array to be filled with filtered data. And then to be fft:d
    # overlap: how many overlapping values between two consecutive fft windows. [in percentage]
    # beta: shape factor for kaiser window.
    # returns:
    # freq: corresponding frequency array
    # fft_signal_out: fft:d array

    def windowedFFT(self):
        # window_width = len(fft_window)  # size of each window
        # window_slide = int(np.round(window_width*(1-overlap/100)))  # number of overlapping points

        # print("Window slide: ", window_slide)
        for i in range(self.window_slide):  # fills the fft_window array with window_slide values from filtered queue
            self.fft_window[self.index_fft] = self.HR_filtered_queue.get()
            self.index_fft += 1
            if self.index_fft == self.window_width:
                self.index_fft = 0
        # TODO: Check if necessary. # roll the matrix so that the last inserted value is to the right.
        self.fft_window = np.roll(self.fft_window, -(self.index_fft+1))
        fft_signal_out = self.smartFFT()  # do fft
        # TODO: check if necessayr. # roll the matrix back
        self.fft_window = np.roll(self.fft_window, (self.index_fft+1))

        return fft_signal_out

    ### smartFFT ###
    # input:
    # signal_in: in signal as an array
    # beta: shape factor for the window
    # returns:
    # freq: frequency array [Hz]
    # signal_out: fft of the in signal as an array

    def smartFFT(self):  # "signal_in" is "fft_window"
        # print("In smartFFT")
        # length_seq = len(signal_in)  # number of sequences
        window = np.kaiser(self.length_fft_window, self.beta)  # beta: shape factor
        self.fft_window = np.multiply(self.fft_window, window)

        signal_in_fft = fft(self.fft_window)  # two-sided fft of input signal

        signal_fft_abs = np.abs(np.divide(signal_in_fft, self.length_fft_window))
        signal_out = np.multiply(2, signal_fft_abs[0:self.length_fft_window//2])  # one-sided fft

        # frequency array corresponding to frequencies in the fft
        return signal_out

    def findPeaks(self, FFT_averaged):
        # Lower and higher freq for removing unwanted areas of the FFT
        # TODO Unsure about this part, same max freq several times in a row
        F_scan_lower = 0.8
        F_scan_upper = 3
        FFT_in_interval = FFT_averaged[self.freq <= F_scan_upper]
        freq2 = self.freq[self.freq <= F_scan_upper]
        FFT_in_interval = FFT_in_interval[freq2 > F_scan_lower]
        peak_freq_linspace = np.linspace(F_scan_lower, F_scan_upper, num=len(FFT_in_interval))

        #print("FFT_in_interval", FFT_in_interval, "\n", len(FFT_in_interval))

        MaxFFT = np.amax(FFT_in_interval)  # Do on one line later, to remove outliers
        #threshold = MaxFFT - 10
        threshold = -27
        peaks, _ = signal.find_peaks(FFT_in_interval)

        index_list = []
        index = 0
        for peak in peaks:
            if FFT_in_interval[peak] < threshold:
                index_list.append(index)
            index += 1
        peaks = np.delete(peaks, index_list)

        #print("Peaks: ",)
        self.peak_freq = []  # Maybe change to array?
        for i in peaks:
            self.peak_freq.append(peak_freq_linspace[i])
        #print("Found peak freq: ", self.peak_freq)

        self.peak_amplitude = []
        for i in peaks:
            self.peak_amplitude.append(FFT_in_interval[i])

        # Plotting for FFT
        self.FFTfreq = peak_freq_linspace
        self.FFTamplitude = FFT_in_interval
        self.len_fft = int(len(FFT_in_interval))
        #print("Length of fft:", self.len_fft)
        return self.peak_freq, self.peak_amplitude

    # TODO Used for plotting in main, remove later
    def getFFTvalues(self):
        return self.FFTfreq, self.FFTamplitude, self.peak_freq, self.peak_amplitude, self.len_fft, self.peak_weighted

    def schmittTrigger(self):
        print("SchmittTrigger started")
        # Test for time
        Inside = True
        # variable declaration
        Tc = 12  # medelvärdesbildning över antal [s]
        schNy = 0  # Schmitt ny
        schGa = 0  # Schmitt gammal
        Hcut = 0.001  # Higher hysteres cut. Change this according to filter. To manage startup of filter
        Lcut = -Hcut  # Lower hysteres cut
        # average over old values. TODO ev. ingen medelvärdesbildning. För att förhindra att andningen går mot ett fast värde. Vi vill se mer i realtid.
        avOver = 5
        freqArray = np.zeros(avOver)  # for averaging over old values
        count = 1  # for counting number of samples passed since last negative flank
        countHys = 1  # for counting if hysteresis should be updated
        FHighRR = 0.7  # To remove outliers in mean value
        FLowRR = 0.1  # To remove outliers in mean value
        # for saving respiratory_queue_RR old values for hysteresis
        trackedRRvector = np.zeros(self.sample_freq * Tc)  # to save old values

        while self.go:
            # to be able to use the same value in the whole loop
            if self.time_when_sent_last_value is not None and (time.time() - self.time_when_sent_last_value > 10):
                # sends zero as breath rate if no value was found the last ten seconds
                self.bluetooth_server.write_data_to_app(0, 'breath rate')
                self.time_when_sent_last_value = time.time()
            trackedRRvector[countHys - 1] = self.RR_filtered_queue.get()
            # self.RTB_final_queue.put(trackedRRvector[countHys - 1])

            if countHys == self.sample_freq * Tc:
                Hcut = np.sqrt(np.mean(np.square(trackedRRvector)))*0.7  # rms of trackedRRvector
                # Hcut = 0.002
                Lcut = -Hcut
                # print("Hcut: ", Hcut)       # se vad hysteres blir
                # print("The last value of vector {}".format(trackedRRvector[countHys-1]))
                # TODO Hinder så att insvängningstiden för filtret hanteras
                countHys = 0

            # schNy = schGa   behövs inte. Görs nedan

            # trackedRRvector[countHys-1] is the current data from filter
            # Takes long time to go into this loop
            if trackedRRvector[countHys - 1] <= Lcut:
                schNy = 0
                if schGa == 1:
                    # print("Inside update resprate loop")
                    np.roll(freqArray, 1)
                    # save the new frequency between two negative flanks
                    freqArray[0] = self.sample_freq / count
                    # Take the mean value
                    # RR_final_queue is supposed to be the breathing rate queue that is sent to app
                    # self.RR_final_queue.put(self.getMeanOfFreqArray(freqArray, FHighRR, FLowRR))
                    # start = time.time()
                    self.bluetooth_server.write_data_to_app(
                        self.getMeanOfFreqArray(freqArray, FHighRR, FLowRR), 'breath rate')
                    self.time_when_sent_last_value = time.time()
                    # done = time.time() # verkar ta lite tid, troligtvis på grund av getMeanOfFrequency
                    # print('send to app', (done - start)*1000)

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
            # print("Tid genom schmittTrigger: ", end-start)

        print("out of schmittTrigger")

    # Used in schmittTrigger. Removes outliers and return mean value over last avOver values.
    def getMeanOfFreqArray(self, freqArray, FHighRR, FLowRR):  # remove all values > FHighRR and < FLowRR
        self.time = time.time()
        # print("Since last time {}".format(self.time - self.last_time))
        self.last_time = self.time
        start = time.time()
        # freqArrayTemp = [x for x in freqArray if (x < FHighRR and x > FLowRR)]
        index_list = []
        index = 0
        # print("Before removal: Array {} \n Low and high hyst {},{}".format(freqArray, FLowRR, FHighRR))
        for freq_value in freqArray:
            if freq_value < FLowRR or freq_value > FHighRR or freq_value == 0:
                index_list.append(index)
            index += 1
        freqArrayTemp = np.delete(freqArray, index_list)
        # print("After removal but before deviation: ", freqArrayTemp)
        # freqArrayTemp = [x for x in freqArrayTemp if x != 0]
        # print(non_zero_temp)
        # print(type(non_zero_temp))
        # freqArrayTemp = freqArrayTemp[non_zero_temp]
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
        # print("Last array before mean value {}".format(freqArrayTemp))
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
        mean = int(np.round(mean))
        # print("data from schmitt {}".format(mean))
        end = time.time()
        # print("Time through getMeanFreq {}".format(end-start))
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
