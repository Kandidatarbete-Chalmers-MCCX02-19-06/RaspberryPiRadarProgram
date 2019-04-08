function [f_search,P_sum_N,f_fine] = basetone_finder(f,FFT_SS,Fs,Fscan_min,Fscan_max,BW_comb,N_harmonics,plot_selection)
%Finds fundamental tone in noisy data by looking at harmonics
%   Looks for fundamental tone with the most energy in it and it's
%   harmoincs.
% f frequency vector.
% FFT, single side FFT... (w>0)
% Fs sampling rate.
%Fscan_min/max, upper lower band where the fundamental is
%BW_comb how tight the scan is done, tighter allows more closely spaced
%error tones.

%F resolution
L_fft = length(FFT_SS)*2;
%Comb bandwidth in samples
i_BW_ss = round(L_fft/Fs*BW_comb/4);%bandwidth in number of frequency samples.
%Limits Fmin/max to protect against index out of bounds from harmonics
Fscan_min = min(Fs/2/N_harmonics,Fscan_min);
Fscan_max = min(Fs/2/N_harmonics,Fscan_max);
%Index of bandwidth to be scanned
i_Fmin = round(Fscan_min*L_fft/Fs);
i_Fmax = round(Fscan_max*L_fft/Fs);
%Number of scans and frequencies to be scanned + their indexes
N_f = round( (i_Fmax - i_Fmin)/i_BW_ss/2 );
%f_search = linspace(Fscan_min,Fscan_max,N_f);
%i_f_search = i_Fmin + (0:(N_f-1))*i_BW_ss*2;

%test
i_f_search = round(i_Fmin:i_Fmax);%blir inte heltal i rad 34???! 
f_search = f(i_f_search);



for i = 1:length(i_f_search)
    P_sum_N(i) = 1;
    for i_harm = 1:N_harmonics
        %Snittar värde
        %P_sum_N(i) = P_sum_N(i) + mean( i_harm*FFT_SS(i_f_search(i)-i_BW_ss: i_harm*i_f_search(i)+i_BW_ss ) );
        
        S_square = FFT_SS(i_harm*(i_f_search(i)-i_BW_ss): i_harm*(i_f_search(i)+i_BW_ss) );
        
        %P_sum_N(i) = P_sum_N(i) +  sqrt( mean( S_square ) );
        P_sum_N(i) = P_sum_N(i) *  sqrt( mean( S_square ) );
    end
    

end

%Abs val incase of complex FFT used
P_sum_N = abs(P_sum_N);

%normalize
P_sum_N = P_sum_N./mean(P_sum_N);

[maxval,i_crude] = max(P_sum_N);%Finds index of crude measurement of frequency.
f_crude = f_search(i_crude);%Crude frequency measurement
%Change to peak finding.... (test)
height = 0.05*(max(P_sum_N)-min(P_sum_N));
height = 0;

%Find peak instead of max val..
[PKS,LOCS]= findpeaks(P_sum_N,'MinPeakProminence',height);
[maxval,i_crude] = max(PKS);
f_crude = f_search(LOCS(i_crude));
%If no peaks, set to 0
if size(f_crude) == [0 1]
    f_crude = 0
end

%Find peak in FFT for fine reading
%[PKS,LOCS]= findpeaks(FFT_SS);
%Finds peak with f closest to crude frequency measurement
%[minval,i_fine] = min( abs( f(LOCS) - f_crude ) );
%Sets f_fine to be fine measuremed value
%f_fine = f(LOCS(i_fine));

%better estimation
%f_fine = HR_estimator(f_search,P_sum_N);

%test to avoid half tone detection instead of directly estimating the
%frequency
f_fine = trueToneFinder(f_search,P_sum_N);


if plot_selection
    %Plots function if chosen
    figure
    plot(f_search*60,P_sum_N)
    xlabel('F [BPM]')
    ylabel('Mean power in signal and its N harmonics')
end


end

