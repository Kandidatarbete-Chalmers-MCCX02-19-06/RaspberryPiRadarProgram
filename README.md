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


## Licence
MIT License

Copyright (c) 2019 Albin Warnicke, Erik Angert Svensson, Julia Nystrand, Simon Nordenström, Emil Johansson och Sebastian Göbel

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
