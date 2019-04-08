function [f_estimated] = HR_estimator(f,FoM)
%Takes array of figure of merit of frequency where a higher figure means
%higher probability of the heartbeat lying at this frequency.
%   
FoM = FoM / mean(FoM);%Normalize

%Remove outliars would be interesting
weights = exp(FoM.^2);%Since FoM is prop. to sqrt(P) times sqrt(P) of harmonics.
weights_avg = mean(weights);%For normalizing.
%simple test without removing outliars
f_estimated = mean(f.*weights/weights_avg);


end

