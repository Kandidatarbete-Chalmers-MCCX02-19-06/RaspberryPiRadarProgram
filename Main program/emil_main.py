from typing import Any, Union

import time
import threading
import numpy as np
import queue

import Radar
import bluetooth_app

# Bluetooth imports
import bluetooth
import math
import random


def main():
    radar_queue = queue.Queue()
    interrupt_queue = queue.Queue()
    send_to_app_queue = queue.Queue()
    # heart_rate_queue = queue.Queue()
    # resp_rate_queue = queue.Queue()

    radar = Radar.Radar(radar_queue, interrupt_queue)
    radar.start()

    bvme = bluetooth_app.bluetooth_app(send_to_app_queue, radar_queue)
    bvme.app_data()
    time.sleep(300)
    print("Radar exit")
    interrupt_queue.put(1)


if __name__ == "__main__":
    main()
