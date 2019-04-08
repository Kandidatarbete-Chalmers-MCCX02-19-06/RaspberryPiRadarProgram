function [t,target_amplitude, target_phase, target_distance] = target_tracker_2(t,dist,amplitude,phase,start_distance,N_avg)
%target_tracker_1, tracks a target and displays distance, amplitude and
%phase.
%   target_tracker_1, tracks the target closest to start_distance over the
%full length of the data and computes the reflection amplitude/phase and
%distance over time
    t_sim_start = datetime('now');
    L_data = length(amplitude(1));
    L_t = length(t)
    N_avg = N_avg%number of samples averaged for choosing the next index
    
    i_peaks = zeros(1,L_data);%Filled with indexes of detected indexes of peaks
    i_peaks_filtered = [];%Filled with filered peak index, is the one used to predict direction
    
    %Find closest distance to starting distance, to find index and protect
    %against out of range input
    [minimum,I] = min( abs(dist-start_distance) );
    i_peaks(1) = I;
    
    %Find closest peak to the starting distance, used to choose
    %which peak to start tracking
    [pks,locs,w,p] = findpeaks(amplitude(1,:));
    [minimum,I] = min( abs(locs-i_peaks(1)) );
    i_peaks(1) = locs(I);
    i_peaks_filtered(1) = locs(I);
    
    %Sets outputs after found index
    target_amplitude(1) = amplitude(1,i_peaks(1));
    target_phase(1) = phase(1,i_peaks(1));
    target_distance(1) = dist(i_peaks(1));
    
    
    for i = 2:L_t
        [pks,locs,w,p] = findpeaks(amplitude(i,:));
        [minimum,I] = min( abs(locs-i_peaks_filtered(i-1)) );
        %i_peaks(i) = round (locs(I) + w(I)/2 );
        %i_peaks(i) = max( min( L_data,i_peaks(i) ) , 1 );
        
        %Test without width of peak being used
        if (size(locs) == [1 0]) | (size(locs) == [0 1])
            %No peaks to be found, data is totally blank
            %just let distance stay, will show target ref going to 0
            i_peaks(i) = i_peaks(i-1);
        else
            i_peaks(i) = locs(I);
        end
        %end of test
        
        %Filter the index
        i_avg_start = max(1,i-N_avg);%Protects against index out of range
        i_peaks_filtered(i) = round( mean(i_peaks(i_avg_start:i)) );%Filtered index
        
        target_amplitude(i) = amplitude(i,i_peaks_filtered(i));
        target_phase(i) = phase(i,i_peaks_filtered(i));
        target_distance(i) = dist(i_peaks_filtered(i));

    end
    
    
    
    T_tracking_duration = datetime('now') - t_sim_start
%Improvement list:
%Find better algorythm instead of findpeaks
%Make output, amp, phase be avg of a set of samples or the peak width
%Filter indexes?? Check constant error from this data..

end

