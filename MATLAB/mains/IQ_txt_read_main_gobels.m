addpath(genpath(pwd))
addpath('Dataread')
addpath('tracker')
addpath('Radar_pulse_watch_and_EKG')
addpath('2019-04-16')

clc
clear all
format shorteng

%Reading of Radar data
%filename_radar = 'Manniska_1m_0305_Test1.csv'
%filename_radar = 'Manniska_lang_0305_Test2.csv'
%filename_radar = 'PulsMetern_0313_Test1.csv'
%filename_radar = 'Lins50cmPuls0328_Test1.csv'
filename_radar = 'PulsLowerGain_EKG_Test1_0416.csv'
[dist,amp, phase,t,gain, L_start, L_end, L_data, L_seq, Fs] = IQ_read_3(filename_radar);

%Reading of wristband pulse measurements
%filename_pulsemeter = 'PulsMetern_0313_Test1.tcx'
%filename_pulsemeter = 'Lins50cmPuls_0328_Test1.tcx'
filename_pulsemeter = 'PulsLowerGain_EKG_Test1_0416.tcx'
[AvHR, MaxHR, HR, tHR] = Read_Pulse(filename_pulsemeter,false);

filename_EKG = "EKG_PulsLowerGain_EKG_Test3_0416.csv";
[T_EKG,F_EKG] = EKG_read(filename_EKG,'HP',false);
HR_EKG = 60*F_EKG;

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
start_distance = 0.6%m
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

% %surf test
% figure(2)
% surf(T,D,A)
% ylabel('Distance [m]')
% xlabel('Time [s]')
% zlabel('Reflection amplitude')
%
% figure(3)
% surf(T,D,P)
% ylabel('Distance [m]')
% xlabel('Time [s]')
% zlabel('Reflection phase [rad]')

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

F_low_HR = 0.9
F_high_HR = 6

BWrel_transband_BR = 0.5
BWrel_transband_HR = 0.1
Atten_stopband = 20 %(!)

[delta_distance_BR] = bandpassfilter(target_delta_distance,Fs,F_low_BR,F_high_BR,BWrel_transband_BR,Atten_stopband);
[delta_distance_HR] = bandpassfilter(target_delta_distance,Fs,F_low_HR,F_high_HR,BWrel_transband_HR,Atten_stopband);

%FFTs
%F_resolution = 0.01 %[Hz]
F_resolution = 5/60 %[Hz]
beta = 0.7
[f_BR,delta_distance_BR_FFT] = smartFFT_abs(delta_distance_BR,Fs,F_resolution,beta);
[f_HR,delta_distance_HR_FFT] = smartFFT_abs(delta_distance_HR,Fs,F_resolution,beta);

%Plots
figure(5)
subplot(2,2,1)
plot(f_BR,log10(delta_distance_BR_FFT))
ylabel('FFT of HR spectrum [m]')
xlabel('f [Hz]')
xlim([F_low_BR F_high_BR])

subplot(2,2,2)
plot(f_HR,log10(delta_distance_HR_FFT))
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
T_resolution = 25 % Time resolution[s]
overlap = 90% overlap of slidiing frames [%]
S_leakage = 0.1 % Leakage from tones 

%test with overtone finder
Fscan_lower_HR = 50/60
Fscan_upper_HR = 160/60
BW_comb =5/60
N_harmonics = 2

%tracking parameters
f0_tracking = 140/60%Guessed frequency to track
B_tracking = 20;
tao_tracking = 60/60%Time cosntant for tracking

[T,BPM_search,FoM_log,f_found] = pulseTrack(delta_distance_HR,Fs,Fscan_lower_HR, Fscan_upper_HR, BW_comb, N_harmonics, T_resolution,overlap,S_leakage,f0_tracking,B_tracking,tao_tracking);

Tao = 5%s
ThrowawayFactor = 10

HR_found = f_found*60;
HR_filtered = pulseFilter(T,HR_found,Tao,ThrowawayFactor);

figure(8)
pcolor(T,BPM_search,FoM_log);
colorbar
xlabel('Time [s]')
ylabel('Frequency [Bpm]')
ylim([Fscan_lower_HR*60 Fscan_upper_HR*60])
hold on
plot(tHR,HR,'r','LineWidth',2)
plot(T,HR_found,'--b','LineWidth',2)
plot(T,HR_filtered,'-.go')
legend('FFT of radar data','Pulse watch reference','Estimated pulse from radar','Filtered radar estimation')
title('Probability map of radar data vs excerice watch')

%plot of BPM over time
figure(9)
plot(T,HR_found,'-.r*')
hold on
plot(tHR,HR)
plot([min(tHR) max(tHR)],[AvHR AvHR],'--r')
plot(T,HR_filtered,'-.b*')
plot(T_EKG,HR_EKG)
legend('Radar','Pulse watch','Average from pulse watch','Filtered Radar','EKG')
xlabel('Time [s]')
ylabel('Frequency [Bpm]')
%ylim(60*[Fscan_lower_HR Fscan_upper_HR])

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









