function [S_o] = filter_BR(S_i,Fs,Q)
%This function detects and removes the breathing and all it's harmonics,
%assuming it's the strongest tone.
%   Detailed explanation goes here
    F_resolution = 1/60;
    beta = 0.1;
    [f,S_i_fft] = smartFFT_abs(S_i,Fs,F_resolution,beta);
    %Does an FFT on the input signal to detect the strongest signal
    
    %[val_mins,I_mins] = max(S_i_fft);
    [PKS,I_peaks]= findpeaks(S_i_fft);
    
    [val_max,I_max] = max(PKS);
    
    i_max = I_peaks(I_max(1));
    f_max = f(i_max)
    %choose the first maximum value to remove it and it's harmonics
    
    %f_max = 1
    %disp('testar med endast 1Hz, obs utan detektering')
    
    order = round(Fs/f_max);
    bw = (f_max/(Fs/2))/Q;
    [b,a] = iircomb(order,bw,'notch'); % Note type flag 'notch'
    %fvtool(b,a);
    
    S_o = filter(b,a,S_i);
    
    

end

