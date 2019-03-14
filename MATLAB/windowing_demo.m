clc
clear all
f = 1 %[Hz]
Fs = 10
F_resolution = 1e-3
%different signal lengths
T1 = 5
T2 = 15
T3 = 30
T4 = 100


N1 = round(T1*Fs);
N2 = round(T2*Fs);
N3 = round(T3*Fs);
N4 = round(T4*Fs);
%Signal
funk = @(t)cos(2*pi*f*t)

%different timespaces
t1 = linspace(0,T1,N1);
t2 = linspace(0,T2,N2);
t3 = linspace(0,T3,N3);
t4 = linspace(0,T4,N4);

%Signals
V1 = funk(t1);
V2 = funk(t2);
V3 = funk(t3);
V4 = funk(t4);

%Get ffts
[f1,S_1] = smartFFT_abs(V1,Fs,F_resolution);
[f2,S_2] = smartFFT_abs(V2,Fs,F_resolution);
[f3,S_3] = smartFFT_abs(V3,Fs,F_resolution);
[f4,S_4] = smartFFT_abs(V4,Fs,F_resolution);

S_1 = 20*log10(S_1);
S_2 = 20*log10(S_2);
S_3 = 20*log10(S_3);
S_4 = 20*log10(S_4);

figure(1)
plot(f1,S_1)
hold on
plot(f2,S_2)
plot(f3,S_3)
plot(f4,S_4)

legend('Nperiods = 5','Nperiods = 15','Nperiods = 30','Nperiods = 100')