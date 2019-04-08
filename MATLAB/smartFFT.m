function [f,S_o] = smartFFT(S_i,Fs,F_resolution,beta)
%Outputs a frequency vector and the amplitude of a SSB FFT of the signal
%with desired minimum frequency resolution
%   Outputs the complex amplitude of a single side band FFT and the frequency
%   vector, for a given minimum frequency resolution.


L_seq = length(S_i);
% %Window here
w = kaiser(L_seq,beta);
S_i = S_i .* w';

%FFT
L_fft = 2 * round (max(Fs/F_resolution,L_seq)/2 )%needed length of FFT, or orignial.
f = Fs*(0:(L_fft/2))/L_fft;

Y = fft(S_i,L_fft);
P2 = Y/L_fft;
P1 = P2(1:L_fft/2+1);
P1(2:end-1) = 2*P1(2:end-1);

S_o = P1;%FFT for delta distance from phase of target



end

