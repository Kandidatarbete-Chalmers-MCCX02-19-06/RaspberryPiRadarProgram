%test of tone detection with fake data

clc
clear all
format shorteng
Fs = 20
T_sample = 300% seconds of sampled data
L_seq = round(T_sample*Fs)%number of samples

SNR = -10%dB
%time base
t = 1/Fs * (0:L_seq-1);

%frequency function
f0_start = 1.1
f0_end = 2.2
K = (f0_end-f0_start)/T_sample

f0 = @(t) f0_start + t*K
%f0 = @(t) f0_start - (f0_end-f0_start)/T_sample*2.*t.*(1-heaviside(t - T_sample/2))

f2 = 1.3
f3 = 0.9
f4 = 2.3

target_delta_distance = 5e-6*sin(2*pi.*(f0_start.*t + K/2.*t.^2));%base

%target_delta_distance = target_delta_distance + 4e-6*cos(2*pi*2*f0(t).*t);% 2nd harmonic
%target_delta_distance = target_delta_distance + 3e-6*cos(2*pi*3*f0(t).*t);% 3rd harmonic

target_delta_distance = awgn(target_delta_distance,SNR,'measured');%noise
%target_delta_distance = target_delta_distance + 7e-6*cos(2*pi*f2*t);%Random tone
%target_delta_distance = target_delta_distance + 3e-6*cos(2*pi*f3*t);%Random tone
%target_delta_distance = target_delta_distance + 8e-6*cos(2*pi*f4*t);%Random tone


target_delta_distance_withnoise = target_delta_distance;




%test of filter on delta distance
F_low_1 = 0.7
F_low_2 = 0.85

F_high_1 = 6
F_high_2 = 7
Atten_stopband = 40
%target_delta_distance = highpass(target_delta_distance,F_low,Fs);
%target_delta_distance = lowpass(target_delta_distance,F_high,Fs);

%Kaiser filter test start
LpFilt = designfilt('lowpassfir', ...
                    'PassbandFrequency',F_high_1, ...
                    'StopbandFrequency',F_high_2, ...
                    'PassbandRipple',0.1, ...
                    'StopbandAttenuation',Atten_stopband, ...
                    'SampleRate',Fs, ...
                    'DesignMethod','kaiserwin');
                
HpFilt = designfilt('highpassfir', ...
                    'PassbandFrequency',F_low_2, ...
                    'StopbandFrequency',F_low_1, ...
                    'PassbandRipple',0.1, ...
                    'StopbandAttenuation',Atten_stopband, ...
                    'SampleRate',Fs, ...
                    'DesignMethod','kaiserwin');
                %fvtool(HpFilt)
%target_delta_distance = filter(LpFilt,target_delta_distance);
%target_delta_distance = filter(HpFilt,target_delta_distance);



FFT_resolution = 0.001%[Hz resolution]
beta = 0.1
[f,target_delta_distance_fft] = smartFFT_abs(target_delta_distance,Fs,FFT_resolution,beta);


figure(1)
plot(f,target_delta_distance_fft)
xlabel('Frequency [Hz]')
ylabel('Amplitude [m]')


disp('test of f')
Fscan_min = 0.9
Fscan_max = 2
BW_comb = 1/60
N_harm = 3
[f_search,P_sum_N,f_fine] = basetone_finder(f,target_delta_distance_fft,Fs,Fscan_min,Fscan_max,BW_comb,N_harm,true);

f_fine = f_fine


%Test of pspectrum
T_resolution = 20 % Time resolution[s]
overlap = 90% overlap of slidiing frames [%]
S_leakage = 0.6 % Leakge from tones 


%[P,F,T] = pspectrum(target_delta_distance,Fs,'spectrogram', ...
%     'TimeResolution',T_resolution,'Overlap',overlap,'Leakage',S_leakage);
[P,F,T] = windowedFFT(target_delta_distance,Fs,T_resolution,overlap,S_leakage);

figure(2)
pcolor(T,F,P);
colorbar
xlabel('Time [s]')
ylabel('Frequency [Hz]')
hold on
plot(T,f0(T),'r','LineWidth',1)



%%
figure(2)
plot(f_search,P_sum_3)
xlabel('Frequeny')
ylabel('Mean value of the three first harmonics')

disp('Recreate')
%Test to recreate signal.
BW_comb = 0.05 %[Hz]

S_filtered = bandpass(target_delta_distance_withnoise,[f_fine-BW_comb f_fine+BW_comb],Fs);
S_filtered = S_filtered + bandpass(target_delta_distance_withnoise,[2*f_fine-BW_comb 2*f_fine+BW_comb],Fs);
S_filtered = S_filtered + bandpass(target_delta_distance_withnoise,[3*f_fine-BW_comb 3*f_fine+BW_comb],Fs);
S_filtered = S_filtered + bandpass(target_delta_distance_withnoise,[4*f_fine-BW_comb 4*f_fine+BW_comb],Fs);
S_filtered = S_filtered + bandpass(target_delta_distance_withnoise,[5*f_fine-BW_comb 5*f_fine+BW_comb],Fs);
figure(3)
subplot(1,2,1)
plot(t,S_o)
hold on
plot(t,target_delta_distance_withnoise)

legend('Original','With tones & noise')
xlabel('Time [s]')
ylabel('Signal [m]')


subplot(1,2,2)
plot(t,S_o)
hold on
plot(t,S_filtered)

legend('Original','Restored')
xlabel('Time [s]')
ylabel('Signal [m]')










