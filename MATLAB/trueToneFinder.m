function [f_true] = trueToneFinder(f,FoM)
%Takes Fom over frequency and finds the most likely true tone, taking into
%account the possibility of strong false tones of half the frequency caused
%by 1/f noise. 
%   Input f in rising order: [1 2 3 4] Hz and FoM in the same order, note
%   they both have to be the same length!
    
    BW_filter = 5/60;%Filter bandwidth [Hz]
    f_res = f(2)-f(1);%Frequency resolution [Hz]
    N_filter =  BW_filter / f_res;%Length of filter in [indexes]
   
    
    %Margin for definining half of frequency span
    f_max = f(end);
    f_min = f(1);
    f_margin = 0.1*(f_max-f_min);
    
    %Index for border between upper and lower span
    i_upper_start = round((f_max/2-f_margin-f_min)/f_res) %defines the start of the upper span, depends on the max,min pulse range settings
    if i_upper_start > 0
       f_upper_start = f(i_upper_start);
    else
        %no chance of false tones
        f_upper_start = length(f);
    end
    
    %Frequency tolerance between expected tone and detected upper tone.
    f_tolerance = 40/60;
    
    %Margin for amplitude
    ampRatioErrorLog_tolerance = 10;
    
    
    FoM_filtered = movmean(FoM,N_filter);
    %Filtered FoM, blurring the FFT so more broadly showing the peaks
    %of energy rather than exact frequencies.
    
    [PKS,LOCS]= findpeaks(FoM_filtered);
    %Now LOCS contains the indexes of all the peaks found in the filtered
    %data
    
    %Find strongest peak, as in the peak with the highest PKS value
    [Y,I] = max(PKS);
    %Now I contains the index(es) of the maximum value
    if size(I) == [1 0]
        f_true = 0;
    
    else
        i_LOCS_max = I(end);%This is the index for the highest peak of the peaks
        i_max = LOCS(i_LOCS_max);%Index for the highest peak

        f_maxPeak = f(i_max);%frequency of peak

        if f_maxPeak < f_max/2-f_margin
            %The detected peak is below half of the highest frequency
            %detectable, this causes a probability of this tone being a false
            %detection of 1/2 of the actual tone

            FoM_filtered_upper = FoM_filtered(i_upper_start:end);
            %Contains only the filtered upper part of the frequency span, to be inspected

            [PKS,LOCS]= findpeaks(FoM_filtered_upper);
            %Now LOCS contains the indexes of all the peaks found in the
            %filtered upper part of the data

            %Find peak closest to double the frequency
            [N_f_error,I] = min( abs(LOCS - 2*i_max) );
            %Now I contains the index(es) of the peaks closest to the expected
            %tone, and N_f_error the number of index deviation from the
            %expected index
            i_LOCS_max = I(end);%This is the index for the highest peak of the peaks
            i_upper_max = LOCS(i_LOCS_max);%Index for the highest peak

            f_upper_maxPeak = f(i_upper_max);%frequency of peak in the upper frequency range

            f_error = abs(N_f_error * f_res);%Difference frequency between expecged peak and found peak in upper range

            %Check amplitude ratio
            ampRatioErrorLog = abs( log10( FoM_filtered(i_upper_max)/FoM_filtered(i_max) ) );%Ratio between upper and lower peaks

            %Check if the upper signal is a a potential candidate for a real
            %signal by comparing the error between the peak and expected peak
            %and amplitude ratio


            %Check frequency difference
            if and((f_error < f_tolerance), (ampRatioErrorLog < ampRatioErrorLog_tolerance))
                %The signal is probably the real one, estimate frequency from
                %this one and report
                disp( ['Error, f:' , num2str(f_error) , 'Amp:' ,num2str(ampRatioErrorLog)] )
                FoM_upper = FoM(i_upper_start:end);
                f_upper = f(i_upper_start:end);
                f_true = HR_estimator(f_upper,FoM_upper);


            else
                %The             %Frequency error is too large, the lower tone can't be half the
                %frequency of this one, suggesting the actual tone is in the
                %lower span. The upper tone is therefore thrown away.

                %The amplitude is too powerful or too weak, most likely too
                %weak, this causes the signal to be unlikely. The upper tone is therefore thrown away. is probably reasonable

                %The frequency error is too large or amplitude too large/small
                %compared to the expected level. This means that the detected
                %tone in the upper range is most likely not a true tone and
                %therefore the output is estimated from the lower span.

                FoM_lower = FoM(1:i_upper_start);
                f_lower = f(1:i_upper_start);
                f_true = HR_estimator(f_lower,FoM_lower);

            end

        else
            %The tone detected is already in the upper range, and there is no
            %lower half tone detected, making this whole program useless...
            %Proceed... Without me...
            f_true = HR_estimator(f,FoM);
        end
    end
    
    
    
    
    
end

