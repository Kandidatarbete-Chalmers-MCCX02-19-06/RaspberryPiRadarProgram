function [S_o] = pulseFilter(T,S_i,Tao,throwawayFactor)
%Moving mean with exclusion of outliars
%   Detailed explanation goes here
Fs = T(2)-T(1);
N_filter = round(Tao*Fs)

sigma = std(S_i);
avg = mean(S_i);
Limit = throwawayFactor*sigma;

for i = 1:length(S_i)
    %Removes outliars for each value
    
    i_start = max(i-N_filter,1);
    %fixes so there's chance of index out of bounds
    
    buffer = S_i(i_start:i);
    %Buffer for sample i
    
    avg_buffer = mean(buffer);
    std_buffer = std(buffer);
    %Average and standard deviation for these N_filter samples
    
    buffer_sans_outliars = buffer( abs(buffer - avg_buffer) < throwawayFactor*std_buffer );
    %removes all samples where the deviation from the mean is more than the
    %given factor amount of standard deviations
    
    if size(buffer_sans_outliars) == [1 0]
        %if empty
        buffer_sans_outliars = 0;
    end
    
    S_o(i) = mean(buffer_sans_outliars);
    %Output average without outliars
    
end

end

