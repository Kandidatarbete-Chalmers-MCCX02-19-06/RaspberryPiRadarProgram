%test of tone detection with fake data

clc
clear all
format shorteng
Fs = 20
T_sample = 20% seconds of sampled data
L_seq = round(T_sample*Fs)%number of samples

SNR_dB = 100%dB
SNR = 10^(SNR_dB/10);

t = 1/Fs * (0:L_seq-1);
f0 = 1

f2 = 1.5
f3 = 0.9
f4 = 2.3
target_delta_distance = 5e-6*cos(2*pi*f0*t);%base
target_delta_distance = target_delta_distance + 4e-6*cos(2*pi*2*f0*t);% 2nd harmonic
target_delta_distance = target_delta_distance + 3e-6*cos(2*pi*3*f0*t);% 3rd harmonic

target_delta_distance = 5e-6 *square(2*pi*t*f0);
S_o = target_delta_distance;

target_delta_distance = awgn(target_delta_distance,SNR);%noise
target_delta_distance = target_delta_distance + 2e-6*cos(2*pi*f2*t);%Random tone
target_delta_distance = target_delta_distance + 1e-6*cos(2*pi*f3*t);%Random tone
target_delta_distance = target_delta_distance + 2e-6*cos(2*pi*f4*t);%Random tone


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
target_delta_distance = filter(LpFilt,target_delta_distance);
target_delta_distance = filter(HpFilt,target_delta_distance);

%Windowing
W = window(@flattopwin,1,L_seq)';
%target_delta_distance = target_delta_distance .* W;


%Padded FFT
FFT_resolution = 0.001%[Hz resolution]
L_fft = max(Fs/FFT_resolution,L_seq)%needed length of FFT, or orignial.
f = Fs*(0:(L_fft/2))/L_fft;

Y = fft(target_delta_distance,L_fft);
P2 = abs(Y/L_fft);
P1 = P2(1:L_fft/2+1);
P1(2:end-1) = 2*P1(2:end-1);
target_delta_distance_fft = P1;%FFT for delta distance from phase of target


figure(1)
semilogy(f,target_delta_distance_fft)
xlabel('Frequency [Hz]')
ylabel('Amplitude [m]')


%Finding dominant tone
BW = 0.05% [Hz] bandwidth of peak finding
i_BW_ss = round(L_fft/Fs*BW/2)%bandwidth in number of frequency samples.

%F resolution
F_resolution = Fs/L_fft
%First harmoinc frequency span
Fmin = 0.9
Fmax = 2

%index version
i_Fmin = Fmin*L_fft/Fs
i_Fmax = Fmax*L_fft/Fs

N_f = round( (i_Fmax - i_Fmin)/i_BW_ss/2 )
f_search = linspace(Fmin,Fmax,N_f);
%i_f_search = linspace(i_Fmin,i_Fmax,N_f);
i_f_search = i_Fmin + (0:(N_f-1))*i_BW_ss*2;


for i = 1:length(i_f_search)
    P_sum_3(i) = mean( target_delta_distance_fft(i_f_search(i)-i_BW_ss: i_f_search(i)+i_BW_ss ) );

end


[maxval,i_crude] = max(P_sum_3)%Finds index of crude measurement of frequency.
f_crude = f_search(i_crude)%Crude frequency measurement

%Find peak in FFT for fine reading
[PKS,LOCS]= findpeaks(target_delta_distance_fft);
%Finds peak with f closest to crude frequency measurement
[minval,i_fine] = min( abs( f(LOCS) - f_crude ) )
%Sets f_fine to be fine measuremed value
f_fine = f(LOCS(i_fine))


Fscan_min = 0.9
Fscan_max = 2
BW_comb = 0.05
[f_fine] = basetone_finder(f,target_delta_distance_fft,Fs,Fscan_min,Fscan_max,BW_comb)

figure(2)
plot(f_search,P_sum_3)
xlabel('Frequeny')
ylabel('Mean value of the three first harmonics')


%Test to recreate signal.
BW_comb = 0.01 %[Hz]

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










