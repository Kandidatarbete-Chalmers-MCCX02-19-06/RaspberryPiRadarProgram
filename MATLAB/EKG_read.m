function [T,F_RtoR_movmean] = EKG_read(filename,type_oscilloscope,BOOL_PLOT)
%Function to read oscilliscope data showing EKG amplifier output, very
%beta..
%   

if strcmp(type_oscilloscope,'TEK')| strcmp(type_oscilloscope,'TEKTRONIX')| strcmp(type_oscilloscope,'tek')| strcmp(type_oscilloscope,'tektronix')
    %If the instrument of choice is of Tektronix brand
    %Reads the data
    Ts = csvread(filename,1,1,[1 1 1 1]);%Sample interval 1/Fs
    Fs = 1/Ts
    N = csvread(filename,0,1,[0 1 0 1])%Reads length of data
    t = Ts*(1:L)';%Sets time according to samples as time in CSV is rounded.
    ch1 = csvread(filename,0,4,[0 4 L-1 4]);
elseif strcmp(type_oscilloscope,'HP')| strcmp(type_oscilloscope,'AGILENT')| strcmp(type_oscilloscope,'agilent')
    %The instrument of choice is of Agilent brand
    M = csvread(filename,2,0);
    t = M(:,1);
    ch1 = M(:,2);
    Fs = t(2) - t(1)
    N = length(ch1)
elseif strcmp(type_oscilloscope,'RIGOL')| strcmp(type_oscilloscope,'rigol')
    %If the chosen oscillioscope is of rigol type.
    M = csvread(filename,3,0);
    t = M(:,1);
    ch1 = M(:,2)';
    N = length(ch1)
    t_1 = M(1,1);
    t_N = M(N,1);
    t = linspace(t_1,t_N,N)';
    Fs = 1/(t(2)-t(1))
    
end

%Filter signal
F_low = 0.9
F_high = 20

BWrel_transband = 0.2
Atten_stopband = 40 %(!)

ch1 = bandpassfilter(ch1,Fs,F_low,F_high,BWrel_transband,Atten_stopband);
%Sets starting time to 0
t = t - t(1);
%Moving maximum for trigger level
N_avg = N/10;
ch1_movmax = movmax(ch1,N_avg);


%limit
%A_lim = 0.85*min(ch1_movmax);
A_lim = 2*mean(abs(ch1));

P_lim = A_lim/2

%Find all peaks
[VAL_PKS,I_LOCS] = findpeaks(ch1,'MinPeakHeight',A_lim,'MinPeakProminence',P_lim);
t_LOCS = t(I_LOCS);
N_peaks = length(I_LOCS);

%Find peak 2 peak intervals
T_RtoR = t_LOCS(2:N_peaks) - t_LOCS(1:N_peaks-1);
%time vector is the middle time of each R-R period
T = 1/2*(t_LOCS(2:N_peaks)+t_LOCS(1:N_peaks-1));

%Mov mean of period
T_RtoR_movmean = movmean(T_RtoR,N_peaks/10);

%Freqency 
F_RtoR_movmean = 1./T_RtoR_movmean;
%the output might be flipped, check this..

if BOOL_PLOT == true
    %PLotting of data
    figure
    plot(t,ch1)
    hold on
    plot([t(1) t(N)],[A_lim A_lim],'--')
    plot(t_LOCS,VAL_PKS,'*')
    title('EKG data')
    xlabel('time [s]')
    ylabel('Input [v]')

    %plotting of period data
    figure
    plot(T,T_RtoR,'*')
    hold on
    plot(T,T_RtoR_movmean)
    title('R to R periods')
    xlabel('time [s]')
    ylabel('R to R period [s]')

end

end

