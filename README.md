# RaspberryPiRadarProgram
RaspberryPiRadarProgram is a Python program to run on a Raspberry Pi to measure heart and respiratory rate with a radar. 
The radar is a A111 from Acconeer, which is a 60 GHz pulsed coherent radar system on a sensor board with an associated connector board 
(R112 and XC112 from Acconeer).
From the radar data, the movents of the chest is tracked to obtain the relative movement. 
The respiratory rate is gained with a Schmitt trigger, while the heart rate is obtained with a FFT.
The Python program also includes a Bluetooth server to connect to up to seven smartphones, 
to visually display the measured heart and repsiratory rate. 
An Android applicaiton is available on Google Play at https://play.google.com/store/apps/details?id=com.chalmers.respiradar, 
and the associated source code is available on GitHub at https://github.com/Kandidatarbete-Chalmers-MCCX02-19-06/ResPiRadar.
