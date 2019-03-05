function [T,D,A,P] = SURF_PREP(distance_vector,amp, phase,t)
%Takes data prepared for tracking and prepares it for showing 3D plots
%using SURF
%   Makes 2D grids for 3d display of data
    Fs = 1/(t(2)-t(1));
    L_start = distance_vector(1);
    L_end = distance_vector(end);
    L_data = length(distance_vector);
    
    [L_seq J] = size(amp);
    [T,D] = meshgrid(t,distance_vector);%2D plane, segment number and distances
    for i = 1:L_seq
        A(i,:) = amp(i,:);%amp
        P(i,:) = phase(i,:);%phase
    end
    A = A';
    P = P';
end

