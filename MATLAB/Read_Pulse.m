%Read_Pulse.m, assumes 1 s between data points
function [AvHR, MaxHR, HR, tHR] = Read_Pulse(Pulsefilename,plot_data)
%clf

filename = Pulsefilename;
C = fileread(filename);
D = strfind(C,'<Value>');
E = strfind(C,'</Value>');

if(size(D,2)~=size(E,2))
    disp('Ngt tok med pulsfilen')
    AvHR = 0;
    MaxHR = 0;
    HR = 0;
    tHR = 0;
    return
end

AvHR = str2num(C(D(1)+7:E(1)-1)); %Average HR is first value after <Value> in tcx-file.  
MaxHR = str2num(C(D(2)+7:E(2)-1)); %Max HR is second value in tcx-file


%Pulse = zeros(size(D),1);
for i = 3:size(D,2)
    HR(i-2) = str2num(C(D(i)+7:E(i)-1)); %i-2 because the 1st HR value is after the 3rd <Value> in tcx
end

tHR = 0:size(HR,2)-1;
if plot_data
    figure
    plot(tHR, HR,'r')
    xlabel('Time [s]')
    ylabel('Pulse [BPM]')
end

shg

