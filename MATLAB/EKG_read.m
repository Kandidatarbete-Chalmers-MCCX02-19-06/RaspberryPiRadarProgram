function [T,F_RtoR_movmean] = EKG_read(filename,BOOL_PLOT)
%Function to read oscilliscope data showing EKG amplifier output, very
%beta..
%   

%Reads the data
Ts = csvread(filename,1,1,[1 1 1 1]);%Sample interval 1/Fs
Fs = 1/Ts
L = csvread(filename,0,1,[0 1 0 1])%Reads length of data
t = Ts*(1:L)';%Sets time according to samples as time in CSV is rounded.
ch1 = csvread(filename,0,4,[0 4 L-1 4]);

%Sets starting time to 0
t = t - t(1);
%Moving maximum for trigger level
N_avg = L/10;
ch1_movmax = movmax(ch1,N_avg);


%limit
A_lim = 0.85*min(ch1_movmax);

%Find all peaks
[VAL_PKS,I_LOCS] = findpeaks(ch1,'MinPeakHeight',A_lim);
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


if BOOL_PLOT == true
    %PLotting of data
    figure
    plot(t,ch1)
    hold on
    plot([t(1) t(L)],[A_lim A_lim],'--')
    plot(t_LOCS,VAL_PKS,'*')

    %plotting of period data
    figure
    plot(T,T_RtoR)
    hold on
    plot(T,T_RtoR_movmean)


    %Plotting of frequency data
    figure
    plot(T,F_RtoR_movmean)
end

end

