function [S_o] = bandpassfilter(S_i,Fs,F_low,F_high,BWrel_transband,Atten_stopband)
%Bandpass filters data and returns it
%   Bandpass filters data and returns it using F_low/high as lower/upper
%passband. 
%Transition band is BWrel_transband, for example 0.15 is 15% relative of
%F_low/high respcetivly 
%test of filter on delta distance
F_low_1 = F_low*(1-BWrel_transband);
F_low_2 = F_low;

F_high_1 = F_high;
F_high_2 = F_high*(1+BWrel_transband);
L_seq = length(S_i);%data length in number of samples


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
            
%Delay removal
delay_LP = grpdelay(LpFilt,L_seq,Fs);%number of lags in samples
delay_HP = grpdelay(HpFilt,L_seq,Fs);%Number of lags in samples
delay_filter_total = round(mean(delay_LP + delay_HP)) %number of lags in samples
S_i = [S_i zeros(1,delay_filter_total)];%Pads with zeros to extend data

%use filters to form bandpass filter
S_o = filter(LpFilt,S_i);
S_o = filter(HpFilt,S_o);


%Delay removal
S_o = S_o(delay_filter_total+1:end);


