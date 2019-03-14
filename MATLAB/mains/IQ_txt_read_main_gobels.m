addpath(genpath(pwd))
addpath('Dataread')
addpath('tracker')
clc
clear all
format shorteng
%addpath("IQ Read")
%addpath("Target tracking")

%filename = 'Manniska_1m_0305_Test1.csv'
filename = 'Manniska_lang_0305_Test1.csv'

[dist,amp, phase,t,gain, L_start, L_end, L_data, L_seq, Fs] = IQ_read_3(filename);
gain = gain
L_start = L_start
L_end = L_end
L_data = L_data
L_seq = L_seq
Fs = Fs
c = 3e8;%[m/s] 
fc = 60.5e9;% [Hz]
wavelength = c/fc


%test of matched filter
MF = amp(1,:).*(cos(phase(1,:)) + 1i*sin(phase(1,:)) );%get the first vector for matched filter
MF = flip(MF);
Emf = sum(abs(MF).^2);
%conv(data,filter,SHAPE,'same');

for i = 1:L_seq
    filtered_refl(i,:) = filter(MF,Emf, (amp(i,:).*(cos(phase(i,:)) + 1i*sin(phase(i,:)) ) ));
    i = i + 1;
end

%amp = abs(filtered_refl);
%phase = angle(filtered_refl);

[T,D,A,P] = SURF_PREP(dist,amp, phase,t);


%Detektering och följning utav mål
start_distance = 0.37%m
start_distance = 1%m
N_avg = 10;
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

%surf test
figure(2)
surf(T,D,A)
ylabel('Distance [m]')
xlabel('Time [s]')
zlabel('Reflection amplitude')

figure(3)
surf(T,D,P)
ylabel('Distance [m]')
xlabel('Time [s]')
zlabel('Reflection phase [rad]')


%unwrap test
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
F_high_BR = 0.8

F_low_HR = 0.7
F_high_HR = 6
BWrel_transband_BR = 0.5
BWrel_transband_HR = 0.15
Atten_stopband = 60 %(!)
%Atten_stopband = 60
[delta_distance_BR] = bandpassfilter(target_delta_distance,Fs,F_low_BR,F_high_BR,BWrel_transband_BR,Atten_stopband);
[delta_distance_HR] = bandpassfilter(target_delta_distance,Fs,F_low_HR,F_high_HR,BWrel_transband_HR,Atten_stopband);

%splitting data
% T_start = 50
% T_end = 65
% i_start = round(T_start*Fs);
% i_stop = round(T_end*Fs);
% t = t(i_start:i_stop);
% L_seq = length(i_start:i_stop)
% delta_distance_HR = delta_distance_HR(i_start:i_stop);
% delta_distance_BR = delta_distance_BR(i_start:i_stop);

%FFTs
%F_resolution = 0.01 %[Hz]
F_resolution = 1/60 %[Hz]
[f_BR,delta_distance_BR_FFT] = smartFFT_abs(delta_distance_BR,Fs,F_resolution);
[f_HR,delta_distance_HR_FFT] = smartFFT_abs(delta_distance_HR,Fs,F_resolution);

%delta_distance_HR_FFT = movmean(delta_distance_HR_FFT,25);

%Frequency finding
BW_comb = 2/60 %[Hz] Tightness of tone scanning
BW_comb = 3/60
N_harmonics = 3%number of harmonics to look at, incl fundamental
%Scan span for breating rate
%Fscan_lower_BR = F_low_BR
%Fscan_upper_BR = F_low_BR/3

%Scan span for heartrate
Fscan_lower_HR = 0.75
Fscan_upper_HR = 2.5
%f_detected_BR = basetone_finder(f_BR,delta_distance_BR_FFT,Fs,F_low_BR,F_high_BR,BW_comb)
[f_search,P_sum_N,f_fine] = basetone_finder(f_HR,delta_distance_HR_FFT,Fs,Fscan_lower_HR,Fscan_upper_HR,BW_comb,N_harmonics,true);
f_detected_HR = f_fine
BPM_HR = 60*f_detected_HR

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


%Waterfall FFT plot of HR

figure(6)
T_resolution = 30 % Time resolution[s]
%F_resolution = 1/60*1.5
overlap = 95% overlap of slidiing frames [%]
S_leakage = 0.8 % Leakage from tones 

% [P,F,T] = pspectrum(delta_distance_HR,Fs,'spectrogram', ...
%     'FrequencyResolution',F_resolution,'Overlap',overlap,'Leakage',S_leakage);

[P,F,T] = pspectrum(delta_distance_HR,Fs,'spectrogram', ...
     'TimeResolution',T_resolution,'Overlap',overlap,'Leakage',S_leakage)


pcolor(T,F,log10(P));
%pcolor(P)
colorbar
xlabel('Time [s]')
ylabel('Frequency [Hz]')
ylim([0 6])
F_resolution = F_resolution
T_resolution = T(2)-T(1)

%test with overtone finder
%ADD sliding window data
[f_search,P_sum_N,f_fine] = basetone_finder(F,P(:,1),Fs,Fscan_lower_HR,Fscan_upper_HR,BW_comb,N_harmonics,false);
f_found = f_fine;
P_N = zeros(length(T),length(f_search));
P_N(1,:) = P_sum_N;
BPM_search = f_search'*60;
for i = 2:length(T)
    %Finds fundamental for all time slots..
    [f_search,P_sum_N,f_fine] = basetone_finder(F,P(:,i),Fs,Fscan_lower_HR,Fscan_upper_HR,BW_comb,N_harmonics,false);
    P_N(i,:) = P_sum_N;
    f_found(i) = f_fine;
end



figure(8)
pcolor(T,BPM_search,P_N');
%pcolor(P)
colorbar
xlabel('Time [s]')
ylabel('Frequency [Bpm]')
ylim([40 100])

f_found = f_found';
size(T)
size(f_found)
%Kolla errorbaren om de skall vara halva
E = ones(size(T)).*F_resolution.*60;

figure(9)
errorbar(T,f_found*60,E,'-s','MarkerSize',10,...
    'MarkerEdgeColor','red','MarkerFaceColor','red')
xlabel('Time [s]')
ylabel('Frequency [Bpm]')




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






