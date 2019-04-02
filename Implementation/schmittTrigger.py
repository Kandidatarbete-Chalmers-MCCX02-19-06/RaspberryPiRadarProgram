
import numpy as np
import scipy as sp
import queue
self.counthys = 0
# Fs samplingsfrekvens
# t vektor linspace, mättid

def schmittTrigger(self, respiratory_queue_BR):
    # Variabeldeklarationer
    Tc = 5
    Fs = 20
    schNy = 0       # Schmitt ny
    schGa = 0       # Schmitt gammal
    Hcut = 0.001    # Higher hysteres cut. Change this according to filter
    Lcut = -Hcut   # Lower hysteres cut
    avOver = 30     # average over old values
    freqArray = np.zeros(avOver)      # for averaging over old values
    count = 1       # for counting number of samples passed since last negative flank
    FHighBR = 0.7       # To remove outliers in mean value
    FLowBR = 0.2        # To remove outliers in mean value

   # if np.mod(self.counthys, Fs*Tc) == 0:       # hysteres

    schNy = schGa
    if respiratory_queue_BR.get() <= Lcut:
        schNy = 0
        if schGa == 1:
            np.roll(freqArray, 1)
            freqArray[0] = Fs/count     # save the new frequency between two negative flanks
            # Take the mean value
            CurFreq_queue = getMeanOfFreqArray()        # CurFreq_queue is supposed to be Breathing rate queue that is sent to app
            # TODO put getMeanOfFreqArray() into queue that connects to send bluetooth values instead

def getMeanOfFreqArray():       # remove outliers and return mean value over last avOver values
    freqArrayTemp = [x for x in freqArray if(x < FHighBR and x > FLowBR)]       # remove all values > FHighBR and < FLowBR
    print(freqArrayTemp)
    freqArrayTemp = freqArrayTemp[np.nonzero(freqArrayTemp)]
    print(freqArrayTemp)

    median = np.median(freqArrayTemp)       # median value
    stanDev = np.std(freqArrayTemp)     # standard deviation

    freqArrayTemp = [x for x in freqArrayTemp if (x > median - 3*stanDev and x < median + 3*stanDev)]
    print(freqArrayTemp)
    mean = np.mean(freqArrayTemp)       # mean value of last avOver values excluding outliers
    return mean