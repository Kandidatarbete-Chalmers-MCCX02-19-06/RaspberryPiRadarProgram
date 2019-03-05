function [f_fine] = basetone_finder(f,FFT_SS,Fs,Fscan_min,Fscan_max,BW_comb)
%Finds fundamental tone in noisy data by looking at harmonics
%   Looks for fundamental tone with the most energy in it and it's
%   harmoincs.
% f frequency vector.
% FFT, single side FFT... (w>0)
% Fs sampling rate.
%Fscan_min/max, upper lower band where the fundamental is
%BW_comb how tight the scan is done, tighter allows more closely spaced
%error tones.
disp('starting funk')

%F resolution
L_fft = length(FFT_SS)*2;
%Comb bandwidth in samples
i_BW_ss = round(L_fft/Fs*BW_comb/2);%bandwidth in number of frequency samples.
%Index of bandwidth to be scanned
i_Fmin = round(Fscan_min*L_fft/Fs);
i_Fmax = round(Fscan_max*L_fft/Fs);
%Number of scans and frequencies to be scanned + their indexes
N_f = round( (i_Fmax - i_Fmin)/i_BW_ss/2 );
f_search = linspace(Fscan_min,Fscan_max,N_f);
i_f_search = i_Fmin + (0:(N_f-1))*i_BW_ss*2;


for i = 1:length(i_f_search)
    P_sum_3(i) = mean( FFT_SS(i_f_search(i)-i_BW_ss: i_f_search(i)+i_BW_ss ) );

end


[maxval,i_crude] = max(P_sum_3);%Finds index of crude measurement of frequency.
f_crude = f_search(i_crude);%Crude frequency measurement

%Find peak in FFT for fine reading
[PKS,LOCS]= findpeaks(FFT_SS);
%Finds peak with f closest to crude frequency measurement
[minval,i_fine] = min( abs( f(LOCS) - f_crude ) );
%Sets f_fine to be fine measuremed value
f_fine = f(LOCS(i_fine));



end

