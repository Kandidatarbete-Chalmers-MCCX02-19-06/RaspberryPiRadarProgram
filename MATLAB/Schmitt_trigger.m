%Schmitt trigger
%Skicka in trackad deltadistansvektor, Fs,t

function[R,FinalFreq] = Schmitt_trigger(delta_distance_BR,Fs,t)
x = delta_distance_BR;
Rnow=10e-3;%Initially when filtering
Hcut = Rnow;
Lcut = -Hcut;
R = 0;
Tc = 10; %Time constant: hysteresis is updated every Tc:th second
Freqar = zeros(10,2)

for(j=1:length(x))
    if(mod(j,Fs*Tc)==0) %Update hysteresis every Tc:th second
        Rnow = rms(x(j-Fs*Tc+1:j));
        R = [R;Rnow] %only for test
        Hcut = Rnow;
        Lcut = -Hcut;
    end

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
    
end

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



