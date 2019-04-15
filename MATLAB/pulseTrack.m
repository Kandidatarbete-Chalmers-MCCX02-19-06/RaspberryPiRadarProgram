function [T,BPM_search,FoM_dB,f_found] = pulseTrack(d_relative,Fs,Fscan_lower, Fscan_upper, BW_comb, N_harmonics, T_resolution,overlap,S_leakage,f0_tracking,tao)
%Takes a filtered signal over time and tries to detect and track the
%heartbeat over time
%   Detailed explanation goes here


%Windowed FFT
[P,F,T] = windowedFFT(d_relative,Fs,T_resolution,overlap,S_leakage);

% 
% %Treat each FFT col. with the multiplication process to obtain a reading
% %for each value.
% [f_search,P_sum_N,f_fine] = basetone_finder(F,P(:,1),Fs,Fscan_lower,Fscan_upper,BW_comb,N_harmonics,false);
% f_found = f_fine;
% P_N = zeros(length(T),length(f_search));
% P_N(1,:) = P_sum_N;
% BPM_search = f_search'*60;
% for i = 2:length(T)
%     %Finds fundamental for all time slots..
%     [f_search,P_sum_N,f_fine] = basetone_finder(F,P(:,i),Fs,Fscan_lower,Fscan_upper,BW_comb,N_harmonics,false);
%     P_N(i,:) = P_sum_N;
%     f_found(i) = f_fine;
% end
% 
% FoM_dB = P_N';
% HR_found = f_found*60;


%test with only FFT
HR_found = 0;
FoM_dB = 10*log10( P );%FFT value in dB
BPM_search = F*60;

%Perhaps add a filter in the frequency domain? This to reduce the amount of
%frequency slots.. Makes the picture more visable to as it evens the
%noisefloor significantly.



RBW = F(2) - F(1);

%Test with movmean for each frequency over time
Tao_FFT_filter = 45;
Ts_FFT = T(2) - T(1);%amount of time the FFT shifts each time.
N_filt = Tao_FFT_filter/Ts_FFT;
FoM_dB = movmean(FoM_dB,N_filt,2);
%to be replaced with exp-forget..

%Declare the weighting function, peaks with a closer to the last value
%are weighted stronger than further away as they are most likely
%outliars
lambda = @(dFrequency,tao) exp(-abs(dFrequency)/tao);

%Tracking algorythm here, this is done cycle by cycle.
f_found = zeros(length(T),1);
for i_cycle = 1:length(T)
   %Cycle loop, repeats once every cycle
   i_Fscan_lower = round( Fscan_lower / RBW );
   i_Fscan_upper = round( Fscan_upper / RBW );
   %Data for this loop, this is done for each finished FFT
   %Throwaway frequency content outside the desired span to be inspected:
   %[Fscan_lower, Fscan_upper]
   T_cycle = T(i_cycle);
   FoM_dB_cycle = FoM_dB(i_Fscan_lower:i_Fscan_upper,i_cycle);
   F_cycle = F(i_Fscan_lower:i_Fscan_upper);
   
   
   
   %start by finding all the peaks and throwing away all below the average
   %value
   %FoM_dB_limit = mean(FoM_dB_cycle); %
   FoM_dB_limit = max(FoM_dB_cycle)-15;
   
   %Find peaks:
   [VAL_peaks,LOC_peaks]= findpeaks(FoM_dB_cycle);
   VAL_peaks_sorted = [];
   LOC_peaks_sorted = [];
   
   %Remove peaks with a peak value of less than the average logvalue (FoM)
   for i = 1:length(VAL_peaks)
        if (VAL_peaks(i) > FoM_dB_limit)
            %value is bigger, add to array
            VAL_peaks_sorted = [VAL_peaks_sorted, VAL_peaks(i)];
            LOC_peaks_sorted = [LOC_peaks_sorted, LOC_peaks(i)];
        end
   end
   
   %Frequencies of the detected peaks
   F_peaks_sorted = F_cycle(LOC_peaks_sorted);
   
   %Delta frequency, fix for first index using the given guess value
   if i_cycle == 1
        %use the input guess frequency
        dF_peaks_sorted = F_peaks_sorted-f0_tracking;
   else
        %Use normal equation
        dF_peaks_sorted = F_peaks_sorted-f_found(i_cycle-1);
   end
   
   %Weights based of lambda
   weighted_peaks = VAL_peaks_sorted + 20*lambda(dF_peaks_sorted,tao);
   [VAL_peak_max,I_peak_max] = max(weighted_peaks);
   f_found(i_cycle) = F_peaks_sorted(I_peak_max(1));
   
   
   
   
   
   
   
   
   
end











end

