function [f_estimated] = HR_estimator(f,FoM)
%Takes array of figure of merit of frequency where a higher figure means
%higher probability of the heartbeat lying at this frequency.
%   
%normalize log FoM
FoM = FoM - min(FoM);
    
    
%Remove outliars would be interesting
%weights = exp(sqrt(abs(FoM)));%Since FoM is prop. to sqrt(P) times sqrt(P) of harmonics.
%weights = exp(log(10)/2*FoM);%Since FoM is prop. to sqrt(P) times sqrt(P) of harmonics.
%weights = FoM.^2;
weights = exp(FoM);
%weights = exp(exp(FoM).^2);
weights_avg = mean(weights)%For normalizing.
%simple test without removing outliars
f_estimated = mean(f.*weights/weights_avg);


end

