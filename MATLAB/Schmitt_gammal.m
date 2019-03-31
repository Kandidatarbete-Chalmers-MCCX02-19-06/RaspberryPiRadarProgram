%Schmitt trigger
%Skicka in trackad deltadistansvektor, Fs,t

function[FinalFreq] = Schmitt_trigger(delta_distance_BR,Fs,t)
x = delta_distance_BR;

Hcut = 1e-3; 
Lcut = -1e-3;

last=0;
N=length(x);
Flank = zeros(length(x),1)';

Sm=zeros(length(x),1)';


for i=1:N

    
    if(last == 0)
      Sm(i)=0;
      
    elseif(last == 1)
      Sm(i)=1;
    end
    

    if (x(i)<= Lcut)
      last=0; 
      Sm(i)=0;

    elseif(x(i)>= Hcut)         
      last=1;  
      Sm(i)=1;

    end
    
    if(i>1 && Sm(i-1)==1 && Sm(i)==0)
        Flank = [Flank i]
    end
    
end

Flank = Flank(Flank~=0)
Indeces = Flank;
Flank = Flank/Fs;
for(i = 1:length(Flank)-1)
    Flank(i) = Flank(i+1)-Flank(i);
end
Flank(end)=[];

Freq = 1./Flank;

FinalFreq = zeros(N);

for(i=1:length(Freq))
    FinalFreq(Indeces(i)) = Freq(i);
end

FinalFreq(FinalFreq == 0) = NaN;
figure(53)
plot(t,FinalFreq,'.','MarkerSize',30)
title('Andningsfrekvens vs. tid')

figure(51)
plot(t,Sm,'blue','LineWidth',3);
title('Schmittad deltadistans vs tid')

figure(50)
plot(t,x,'r','LineWidth',1.5);
title('Deltadistans vs tid')



