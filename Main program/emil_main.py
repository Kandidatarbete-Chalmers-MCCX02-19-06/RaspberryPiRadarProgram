from typing import Any, Union

import time
import threading
import numpy as np
import queue

import Radar
import bluetooth_app        # import bluetooth class
import DataAcquisition      # Import class which collects and filters relevant data.
import SignalProcessing

# Bluetooth imports
import bluetooth
import math
import random
import subprocess       # for Raspberry Pi shutdown


def main():
    # subprocess.call(
    #    "./Documents/evk_service_linux_armv71_xc112/utils/acc_streaming_server_rpi_xc112_r2b_xr112_r2b_a111_r2c")

    radar_queue = queue.Queue()
    HR_filtered_queue = queue.Queue()
    HR_final_queue = queue.Queue()
    RR_filtered_queue = queue.Queue()
    RR_final_queue = queue.Queue()

    #send_to_app_queue = queue.Queue()
    go = ["True"]
    run_measurement = []
    # heart_rate_queue = queue.Queue()
    # resp_rate_queue = queue.Queue()

    # radar = Radar.Radar(radar_queue, go)
    # radar.start()
    dataAcquisition = DataAcquisition.DataAcquisition(go, HR_filtered_queue, RR_filtered_queue)
    dataAcquisition.start()
    signalProcessing = SignalProcessing.SignalProcessing(go, HR_filtered_queue, HR_final_queue, RR_filtered_queue, RR_final_queue)


    # bvme = bluetooth_app.bluetooth_app(radar_queue, run_measurement, go)
    # bvme.app_data()
    # print('End of bluetooth_app')
    time.sleep(300)
    # interrupt_queue.put(1)
    go.pop(0)
    # radar.join()
    dataAcquisition.join()

    print("radar is closed")
    # bvme.connect_device_thread.join()
    print("connect_device is closed")

    print('Shut down succeed')
    #subprocess.call(["sudo", "shutdown", "-r", "now"])


if __name__ == "__main__":
    main()
