import time
import threading
import numpy as np
import queue

import Radar

# Bluetooth imports
import bluetooth
import math
import random

# Bluetooth variables
clientList = []         # list for each connected device, sockets
addressList = []        # list for mac-adresses from each connected device
readThreadList = []     # list for threads to recieve from each device
#sinvalue = 0
run = True
test_queue = queue.Queue()
host = ""
port = 1  # Raspberry Pi uses port 1 for Bluetooth Communication

server = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
print('Bluetooth Socket Created')
try:
    server.bind((host, port))
    print("Bluetooth Binding Completed")
except:
    print("Bluetooth Binding Failed")

print(hex(id(server)))
# Main method for initiating and running radar measurements, signal processing and sending data through bluetooth to application.
def main():
    global server
    global run
    print(hex(id(server)))
    radar_queue = queue.Queue()
    interrupt_queue = queue.Queue()
    # heart_rate_queue = queue.Queue()
    # resp_rate_queue = queue.Queue()

    radar = Radar.Radar(radar_queue, interrupt_queue)
    radar.start()
    time.sleep(10)
    interrupt_queue.put(1)


if __name__ == "__main__":
    main()
