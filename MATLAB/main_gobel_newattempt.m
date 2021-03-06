addpath(genpath(pwd))
addpath('Dataread')
addpath('tracker')
clc
clear all
format shorteng

%Reading of Radar data
filename_radar = 'Lins50cmPuls_0328_Test1.csv'
[dist,amp, phase,t,gain, L_start, L_end, L_data, L_seq, Fs] = IQ_read_3(filename_radar);

%Reading of wristband pulse measurements
%filename_pulsemeter = 'PulsMetern_0313_Test1.tcx'
filename_pulsemeter = 'Lins50cmPuls_0328_Test1.tcx'
[AvHR, MaxHR, HR, tHR] = Read_Pulse(filename_pulsemeter,false);

gain = gain
L_start = L_start
L_end = L_end
L_data = L_data
L_seq = L_seq
Fs = Fs
c = 3e8;%[m/s] 
fc = 60.5e9;% [Hz]
wavelength = c/fc

%Detektering och följning utav mål
start_distance = 0.47%m
N_avg = 100;
[t,target_amplitude, target_phase, target_distance] = target_tracker_2(t,dist,amp,phase,start_distance,N_avg);

figure(1)
subplot(1,2,1)
plot(dist,amp(1,:))
ylabel('Amplitude []')
xlabel('Distance [m]')

subplot(1,2,2)
plot(dist,phase(1,:))
ylabel('phase []')
xlabel('Distance [m]')

%unwrap signal
target_phase = unwrap(target_phase);

%Signal filtreringstest
disp('Downsampling with ratio r:')
r = 1
%Down sampling
target_amplitude = decimate(target_amplitude,r);
target_phase = decimate(target_phase,r);
target_distance = decimate(target_distance,r);
t = decimate(t,r);
L_seq = L_seq/r%new length in time domain
Fs = Fs/r%New sample rate in time domain

%Delta distance of tracked target
target_delta_distance = wavelength/2/pi/2*target_phase;

%filer data into two bandwidths
F_low_BR = 0.2
F_high_BR = 1.2

F_low_HR = 0.2
F_high_HR = 6

BWrel_transband_BR = 0.5
BWrel_transband_HR = 0.1
Atten_stopband = 40 %(!)

[delta_distance_BR] = bandpassfilter(target_delta_distance,Fs,F_low_BR,F_high_BR,BWrel_transband_BR,Atten_stopband);
[delta_distance_HR] = bandpassfilter(target_delta_distance,Fs,F_low_HR,F_high_HR,BWrel_transband_HR,Atten_stopband);

%remove breathing
Q = 5
[delta_distance_HR] = filter_BR(delta_distance_HR,Fs,Q);

%filter again
F_low_HR = 1
[delta_distance_HR] = bandpassfilter(delta_distance_HR,Fs,F_low_HR,F_high_HR,BWrel_transband_HR,Atten_stopband);

%FFTs
%F_resolution = 0.01 %[Hz]
F_resolution = 1/60 %[Hz]
beta = 0.7
[f_BR,delta_distance_BR_FFT] = smartFFT_abs(delta_distance_BR,Fs,F_resolution,beta);
[f_HR,delta_distance_HR_FFT] = smartFFT_abs(delta_distance_HR,Fs,F_resolution,beta);

%Plots
figure(5)
subplot(2,2,1)
plot(f_BR,delta_distance_BR_FFT)
ylabel('FFT of HR spectrum [m]')
xlabel('f [Hz]')
xlim([F_low_BR F_high_BR])

subplot(2,2,2)
plot(f_HR,delta_distance_HR_FFT)
ylabel('FFT of HR spectrum [m]')
xlabel('f [Hz]')
xlim([F_low_HR F_high_HR])

%time 
subplot(2,2,3)
plot(t,delta_distance_BR)
ylabel('Plot of BR bandwidth [m]')
xlabel('Time [s]')

subplot(2,2,4)
plot(t,delta_distance_HR)
ylabel('Plot of HR bandwidth [m]')
xlabel('Time [s]')

%Settings for continuous pulse detection
T_resolution = 30 % Time resolution[s]
overlap = 90% overlap of slidiing frames [%]
S_leakage = 0.86 % Leakage from tones 

%test with overtone finder
Fscan_lower_HR = 60/60
Fscan_upper_HR = 150/60
BW_comb =2/60

[P,F,T] = windowedFFT(delta_distance_HR,Fs,T_resolution,overlap,beta);

Tao = 20%s
ThrowawayFactor = 1
%HR_filtered = pulseFilter(T,HR_found,Tao,ThrowawayFactor);

BPM_search = 60*F;

figure(8)
pcolor(T,BPM_search,10*log10(P));
colorbar
xlabel('Time [s]')
ylabel('Frequency [Bpm]')
ylim([Fscan_lower_HR*60 Fscan_upper_HR*60])
hold on
plot(tHR,HR,'r','LineWidth',2)
title('Probability map of radar data vs excerice watch')

% %plot of BPM over time
% figure(9)
% plot(T,HR_found,'-.r*')
% hold on
% plot(tHR,HR)
% plot([min(tHR) max(tHR)],[AvHR AvHR],'--r')
% plot(T,HR_filtered,'-.b*')
% legend('Radar','Pulse watch','Average from pulse watch','Filtered Radar')
% xlabel('Time [s]')
% ylabel('Frequency [Bpm]')
% ylim(60*[Fscan_lower_HR Fscan_upper_HR])

%Tracked data
figure(10)
subplot(2,2,1)
plot(t,target_amplitude)
xlabel('t [s]')
ylabel('Amplitude of tracked target [arb]')

subplot(2,2,2)
plot(t,target_phase)
xlabel('t [s]')
ylabel('Phase of tracked target [rad]')

subplot(2,2,3)
plot(t,target_distance)
xlabel('t [s]')
ylabel('Distance of tracked target [m]')

subplot(2,2,4)
plot(t,5e-3/2/pi/2*(target_phase - mean(target_phase)))
xlabel('t [s]')
ylabel('Delta distance of tracked target [m]')


%% test of reading EKG data
clc
clear all
addpath('PulsLowerGain_EKG_Test2_0415')
filename = "Erik_EKG_low_0418_EKG.csv"

% %Test without Ts, L
% Ts = csvread(filename,1,1,[1 1 1 1]);%Sample interval 1/Fs
% Fs = 1/Ts
% L = csvread(filename,0,1,[0 1 0 1])%Reads length of data
% t = Ts*(1:L)';%Sets time according to samples as time in CSV is rounded.
% ch1 = csvread(filename,0,4,[0 4 L-1 4]);
% 
% %code to find period
% 
% %Moving maximum for trigger level
% N_avg = 100
% ch1_movmax = movmax(ch1,N_avg);
% 
% 
% %limit
% A_lim = 0.85*min(ch1_movmax);
% 
% %Find all peaks
% [VAL_PKS,I_LOCS] = findpeaks(ch1,'MinPeakHeight',A_lim);
% t_LOCS = t(I_LOCS);
% N_peaks = length(I_LOCS)
% 
% %Find peak 2 peak intervals
% T_RtoR = t_LOCS(2:N_peaks) - t_LOCS(1:N_peaks-1);
% %time vector is the middle time of each R-R period
% T = 1/2*(t_LOCS(2:N_peaks)+t_LOCS(1:N_peaks-1));
% 
% %Mov mean of period
% T_RtoR_movmean = movmean(T_RtoR,N_peaks/10);
% 
% %Freqency 
% F_RtoR_movmean = 1./T_RtoR_movmean;

%Attempt using the function
type_oscilloscope = 'rigol'
[T,F_RtoR_movmean] = EKG_read(filename,type_oscilloscope,true)

%PLotting of data
% figure(1)
% plot(t,ch1)
% hold on
% plot([t(1) t(L)],[A_lim A_lim],'--')
% plot(t_LOCS,VAL_PKS,'*')

%plotting of period data
% figure(2)
% plot(T,T_RtoR)
% hold on
% plot(T,T_RtoR_movmean)


%Plotting of frequency data
figure
plot(T,60*F_RtoR_movmean)

xlabel('time [s]')
ylabel('HR [bpm]')
title('EKG reading')













