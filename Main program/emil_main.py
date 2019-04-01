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


def main():
    radar_queue = queue.Queue()
    send_to_app_queue = queue.Queue()
    a = []
    # heart_rate_queue = queue.Queue()
    # resp_rate_queue = queue.Queue()

    radar = Radar.Radar(radar_queue, a)
    radar.start()

    bvme = bluetooth_app.bluetooth_app(send_to_app_queue, radar_queue)
    bvme.app_data()
    print('Exit starting')
    # time.sleep(300)
    # interrupt_queue.put(1)

    a.append("True")
    radar.join()
    print("radar is closed")
    bvme.connect_device_thread.join()
    print("connect_device is closed")

    subprocess.call(["sudo", "shutdown", "-r", "now"])


if __name__ == "__main__":
    main()
