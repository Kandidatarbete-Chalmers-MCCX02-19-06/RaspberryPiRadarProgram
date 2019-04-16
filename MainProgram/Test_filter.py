import numpy as np
import matplotlib.pyplot as plt
import filter

pkter = 10000
f = 0.4
t = np.linspace(1,100,pkter)

sample_freq = 20
length_seq = 1000
sample_spacing = 1/sample_freq

t = np.arange(length_seq)*sample_spacing

x = np.zeros(len(t))
x[0:round(len(t)/2)] = np.sin(f*2*np.pi*t[0:round(len(t)/2)])+5
x[round(len(t)/2):len(t)] = np.sin(f*2*np.pi*t[round(len(t)/2):len(t)])+2
x = x + np.sin(1*2*np.pi*t)




plt.plot(t,x)
plt.grid()
plt.show()

testfilter_high = filter.Filter('highpass_RR')
testfilter_low = filter.Filter('lowpass_RR')

y = np.zeros(len(x))

for i in range(len(x)):
    y[i] = testfilter_high.filter(x[i])
    y[i] = testfilter_low.filter(y[i])

plt.plot(t,y)
plt.grid()
plt.show()
