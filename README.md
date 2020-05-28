# RaspberryPiRadarProgram
RaspberryPiRadarProgram is a Python program to run on a Raspberry Pi to measure heart and respiratory rate with a radar. The radar is an A111 from Acconeer, which is a 60 GHz pulsed coherent radar system on a sensor board with an associated connector board (R112 and XC112 from Acconeer). From the radar data, the movements of the chest are tracked to obtain the relative movement. The respiratory rate is gained with a Schmitt trigger, while the heart rate is obtained with an FFT. The Python program also includes a Bluetooth server to connect to up to seven smartphones, to visually display the measured heart and respiratory rate. An Android application is available on Google Play at https://play.google.com/store/apps/details?id=com.chalmers.respiradar, and the associated source code is available on GitHub at https://github.com/Kandidatarbete-Chalmers-MCCX02-19-06/ResPiRadar. The Python program needs a package called acconeer-python-exploration-tool to run properly. The Exploration Tool is originally from https://github.com/acconeer/acconeer-python-exploration, but newer versions of it does not work in this project. Therefor a copy of the Exploration Tool is provided in this project. The Exploration Tool could either be placed in the Python Package folder or it could be imported locally by inserting the path in the import statements. The Exploration Tool also have some dependencies that have to be installed, see the requirements.txt in the Exploration Tool. The Raspberry Pi also needs software for connecting to the radar and is available at https://developer.acconeer.com/.

## Source code
The Python program is located in the MainProgram folder. 
Following scripts and modules are available:
- `main.py`\
  Main program to start all threads and services.
- `bluetooth_server_module.py`\
  Module to host the Bluetooth server. Can connect up to seven devices. Every connection starts a new thread to read incoming commands.
- `data_acquisition_module.py`\
  Module to acquire radar data. Tracks the highest peak to calculate relative distance movements from the phase.
- `signal_processing_module.py`\
  Module to signal process the relative movements to obtain heart rate and respiratory rate with Schmitt trigger and FFT.
- `filter.py`\
  Creates a band-pass filter to filter the relative movements.
  
There is also MATLAB files in the folder MATLAB to signal process radar data afterwards.

## Issues
- Only the provided copy of the Exploration Tool can be used (it's possible to adjust the `data_acquisition_module.py` to use newer versions of the Exploration Tool from https://github.com/acconeer/acconeer-python-exploration).
- The exploration Tool must either be placed in the Python package folder or imported by inserting the path in the import statements.
- There can be problem with the Bluetooth and GPIO using the same UART which means they will block each other. This can be solved by changing Bluetooth to use the mini UART. 
- This project is supposed to run on a Raspberry Pi. It might be possible to run it on Windows/Mac too, but it's not guaranteed. If the program is used remotly (not on the Raspberry Pi with the radar) the IP adress in the JSONClient (row 47 in `data_acquisition_module.py`) in has to be changed from the local 0.0.0.0 to the actual adress.

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

Some software in this repository is licensed under other terms and conditions. 
See license files in the subdirectories for the external software components.
