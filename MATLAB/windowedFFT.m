function [P,F,T] = windowedFFT(data_in,Fs,T_resolution,overlap,beta)
%windowedFFT This function computes a FFT with a moving window, similarly
%to what is used in the function pspectrum.
%   Inputs:
%   data_in is the data on which the FFT is performed
%   Fs the sample rate [Hz]
%   T_resolution the time resolution [s]
%   overlap the amount of overlap between windows [%]
%   type_window is a string saying the type of windowing function used 
%
%   Outputs:
%   P is the FFT output value [linear scale]
%   F is the frequency vector 
%   T is the time vector

%Length of data [samples]
L_seq = length(data_in)
%Width of FFT window [samples]
w = round(T_resolution*Fs)
%Amount of samples the center index moves each window.
window_slide = round(w.*(1-overlap/100));
%Number of windows used + 1
N_windows = (L_seq-w/2)/window_slide;
%index of middle sample for each of the windows
center_index = w/2 + (0:N_windows).*window_slide+1;
%Time of middle sample of each of the windows
T = center_index/Fs;
%Calculate the desired frequency resolution to not be overly bottlenecked
%by windowing but not overdone
F_resolution = 0.5/60%JUST FOR TEST (!) To be set according to beta...




for i = 1:(N_windows + 1)
    %Window indexes, moving with i
    %test
    i = i
    i_window_min = center_index(i)-w/2;
    i_window_max = min(center_index(i)+w/2,length(data_in));
    i_window = i_window_min:i_window_max;
    [f,S_o] = smartFFT_abs(data_in(i_window),Fs,F_resolution,beta);
    P(:,i) = S_o;
    
end
F = f;


end

