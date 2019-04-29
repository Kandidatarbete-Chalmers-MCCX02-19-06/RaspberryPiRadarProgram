
# Import available classes used in main
import time
import queue
import subprocess       # For Raspberry Pi shutdown
import os               # For using terminal commands
import matplotlib.pyplot as plt
import numpy as np

# Import our own classes used in main
import bluetooth_server_module          # Import bluetooth class for managing connections with devices
import data_acquisition_module          # Import class which collects and filters relevant data from radar
# Import signal processing class for Schmitt Trigger and Pulse detection
import signal_processing_module


def main():
    # subprocess.call("./Documents/evk_service_linux_armv71_xc112/utils/acc_streaming_server_rpi_xc112_r2b_xr112_r2b_a111_r2c")
    #subprocess.Popen('cd ..', shell=False)
    #evk = subprocess.Popen('./evk_service_linux_armv7l_xc112/utils/acc_streaming_server_rpi_xc112_r2b_xr112_r2b_a111_r2c', shell=False)
    #os.system('gnome-terminal -x ./evk_service_linux_armv7l_xc112/utils/acc_streaming_server_rpi_xc112_r2b_xr112_r2b_a111_r2c')

    #p = os.popen('sudo /home/pi/Documents ls')
    # print(p.read()) # fungerar

    #p = os.popen('sudo lxterminal -e ./home/pi/Documents/evk_service_linux_armv71_xc112/utils/acc_streaming_server_rpi_xc112_r2b_xr112_r2b_a111_r2c')
    # print(p.read())

    # process = subprocess.Popen(
    #     'lxterminal -e "./home/pi/Documents/evk_service_linux_armv71_xc112/utils/acc_streaming_server_rpi_xc112_r2b_xr112_r2b_a111_r2c"',
    #     stdout=subprocess.PIPE,
    #     stderr=None,
    #     shell=True
    # )
    # subprocess.call(["./home/pi/Documents/evk_service_linux_armv71_xc112/utils/acc_streaming_server_rpi_xc112_r2b_xr112_r2b_a111_r2c"],shell=True)

    # process = subprocess.Popen(
    #     'lxterminal -e "ls -ls"',
    #     stdout=subprocess.PIPE,
    #     stderr=None,
    #     shell=True
    # )
    # print(process.stdout)

    # Queues used for accessing data from different threads
    HR_filtered_queue = queue.Queue()
    HR_final_queue = queue.Queue()
    RR_filtered_queue = queue.Queue()
    RR_final_queue = queue.Queue()
    RTB_final_queue = queue.Queue()  # Real time breating final queue

    # List of arguments and data sent between classes
    go = ["True"]       # Used for closing threads before shutdown of Raspberry Pi
    run_measurement = ["value"]        # Determines if data is being sent to devices or not
    sample_freq = 0         # Value is updated in DataAcquisition. Needs to be the same in the whole program
    list_of_variables_for_threads = {"HR_filtered_queue": HR_filtered_queue, "HR_final_queue": HR_final_queue,
                                     "RR_filtered_queue": RR_filtered_queue, "RR_final_queue": RR_final_queue,
                                     "RTB_final_queue": RTB_final_queue, "go": go, "run_measurement": run_measurement,
                                     "sample_freq": sample_freq}
    FFTfreq = [1, 2, 3]
    FFTamplitude = [1, 2, 3]
    peak_freq = [1]
    peak_amplitude = [1]
    array = []

    # BluetoothServer object sent to classes which sends data locally
    bluetooth_server = bluetooth_server_module.BluetoothServer(list_of_variables_for_threads)

    # Starts thread of run() method in DataAcquisition class
    data_acquisition = data_acquisition_module.DataAcquisition(
        list_of_variables_for_threads, bluetooth_server)
    data_acquisition.start()

    # SignalProcessing object used below
    signal_processing = signal_processing_module.SignalProcessing(
        list_of_variables_for_threads, bluetooth_server, FFTfreq, FFTamplitude)

    #plt.pcolormesh(specTime, specFreq, specSignal)
    # plt.pause(1)
    #plt.xlim(1, 3)
    # Lets threads and thereby program run while go is True. Go is set from app
    while list_of_variables_for_threads.get('go'):
        # Test of FFT, remove later
        plt.clf()
        #plt.xlim(1, 3)
        FFTfreq, FFTamplitude, peak_freq, peak_amplitude, peak_weighted = signal_processing.getFFTvalues()
        print("Length of FFT_amplitude", len(FFTamplitude))
        if len(FFTamplitude) == 30:
            array.append(np.transpose(FFTamplitude))
            plt.pcolormesh(array)
        plt.pause(1)
        # plt.plot(FFTfreq, FFTamplitude)
        # plt.plot(peak_freq, peak_amplitude, 'bo')
        # plt.plot(peak_freq, peak_weighted, 'ro')

        # time.sleep(1)
        #print(FFTfreq, FFTamplitude)

    # Waits for running threads to finish their loops
    bluetooth_server.connect_device_thread.join()
    print("bluetooth_server is closed")
    # signal_processings.heart_rate_thread.join()
    signal_processing.schmittTrigger_thread.join()
    print("signal_processing is closed")
    data_acquisition.join()
    print("data_acquisition is closed")

    print('Shut down succeed')
    # subprocess.call(["sudo", "shutdown", "-r", "now"])         # Terminal command for shutting down Raspberry Pi


if __name__ == "__main__":      # Required for making main method the used main-method
    main()
