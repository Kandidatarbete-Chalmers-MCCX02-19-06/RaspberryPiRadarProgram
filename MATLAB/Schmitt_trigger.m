%Schmitt-trigger
%Skicka in trackad deltadistansvektor, Fs,t

function[R,FinalFreq] = Schmitt_trigger(delta_distance_BR,Fs,t)
F_low_BR = 0.2 % Sk in egentligen
F_high_BR = 0.7
x = delta_distance_BR;
Rlowbound=0.1e-3;
Scale = 5;
Rstart = Rlowbound*Scale;
RelRms = 0.5;
Hcut = Rstart;
Lcut = -Hcut;
R = Rstart;
Rnow = Rstart;
Tc = 5; %Time constant: hysteresis is updated every Tc:th second
AvOver = 20;
freqarray = zeros(AvOver,1)
CurrFreq = 0;
Schga = 0;
Schny = 0; 
count = 1;
counthys = 1;
FinalFreq = 0;

figure(79)
h = animatedline('Color','red');
shg
xlabel('Tid [s]')
ylabel('Andningsfrekvens [Hz]')

N=length(x);
for(j=1:N) %Loopen motsvaras av data som fås sekvensvis från radarn
    %if(mod(j,Fs*Tc)==0) %Update hysteresis every Tc:th second

    if(mod(counthys,Fs*Tc)==0)
        Rnow = rms(x(j-Fs*Tc+1:j))*RelRms;
        if(Rnow<Rlowbound)
             Rnow = Rlowbound;
             count = 1;
        end
        R = [R;Rnow]; %only for testing
        Hcut = Rnow;
        Lcut = -Hcut;
        counthys=0;
    end

    Schny = Schga;

    if (x(j)<= Lcut)
      Schny=0;
      if(Schga == 1)
          %Fixa massa och skicka till appen
          %Uppd freqarr (rot och sätt in)
          %MVB och ta bort utstickare
          freqarray = circshift(freqarray,1);
          freqarray(end) = Fs/(count);
          %freqarray
          
          CurrFreq = mean(rmoutliers(nonzeros(freqarray(freqarray <= F_high_BR & freqarray >= F_low_BR))));
         
          count = 0;
      end

    elseif(x(j)>= Hcut)
      Schny=1;
    end

    Schga = Schny;
    count = count + 1;
    counthys = counthys + 1;

    addpoints(h,t(j),CurrFreq)
    pause(0.0001)
    
end

FinalFreq = freqarray; 
R(end) = [];
R = repelem(R,Fs*Tc);

figure(5)
subplot(2,2,3)
plot(t,delta_distance_BR,'b')
hold on
plot(t(1:length(R)),R,'r')
plot(t(1:length(R)),-R,'r');
hold off

