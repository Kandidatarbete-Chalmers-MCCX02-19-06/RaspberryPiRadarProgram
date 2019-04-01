from typing import Any, Union

import time
import threading
import numpy as np
import queue

import Radar
import bluetooth_app        # import bluetooth class

# Bluetooth imports
import bluetooth
import math
import random
import subprocess       # for Raspberry Pi shutdown

go = True


def main():
    global go
    # subprocess.call(
    #    "./Documents/evk_service_linux_armv71_xc112/utils/acc_streaming_server_rpi_xc112_r2b_xr112_r2b_a111_r2c")
    time.sleep(5)

    radar_queue = queue.Queue()
    #send_to_app_queue = queue.Queue()
    a = []
    # heart_rate_queue = queue.Queue()
    # resp_rate_queue = queue.Queue()

    radar = Radar.Radar(radar_queue, go)
    radar.start()

    bvme = bluetooth_app.bluetooth_app(radar_queue, go)
    bvme.app_data()
    print('Exit starting')
    # time.sleep(300)
    # interrupt_queue.put(1)

    # a.append("True")
    radar.join()
    print("radar is closed")
    bvme.connect_device_thread.join()
    print("connect_device is closed")

    print('Shut down succeed')
    #subprocess.call(["sudo", "shutdown", "-r", "now"])


if __name__ == "__main__":
    main()
