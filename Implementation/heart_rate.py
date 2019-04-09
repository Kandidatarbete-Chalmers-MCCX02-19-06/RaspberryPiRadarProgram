import numpy as np
from scipy import signal #Det här kanske behöver importeras på något annat sätt.
import matplotlib.pyplot as plt #TODO: ta bort sen
from scipy.fftpack import fft


# smartFFT returns:
# freq: frequency array [Hz] 
# signal_out: fft-signal array 
def smartFFT(signal_in, sample_freq, beta):
    length_seq = len(signal_in) #number of sequences
    window = np.kaiser(length_seq,beta) #beta: shape factor
    signal_in = np.multiply(signal_in,window) 

    signal_in_fft = fft(signal_in) #two-sided fft of input signal

    signal_fft_abs = abs(signal_in_fft/length_seq)
    signal_out = 2*signal_fft_abs[0:length_seq//2] # one-sided fft 

    freq = sample_freq*np.arange(length_seq/2)/length_seq # frequency array corresponding to frequencies in the fft

    return freq,signal_out


## MAIN ##  TODO: Ta bort MAIN sen
sample_freq = 200
length_seq = 2000
sample_spacing = 1/sample_freq

t = np.arange(length_seq)*sample_spacing
signal_in = 4*np.sin(10.0 * 2.0*np.pi*t) + 0.5*np.sin(80.0 * 2.0*np.pi*t)
beta = 1

[freq,signal_out] = smartFFT(signal_in,sample_freq,beta)

plt.plot(freq, signal_out)
plt.grid()
plt.show()