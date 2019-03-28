import queue
import time
import threading
import bluetooth
import math
import random


class bluetooth_app():
    def constructor(self, send_to_app_queue):
        # Bluetooth variables
        self.client_list = []         # list for each connected device, sockets
        self.address_list = []        # list for mac-adresses from each connected device
        self.read_thread_list = []     # list for threads to recieve from each device

        self.send_to_app_queue = send_to_app_queue
        self.host = ""
        self.port = 1
        self.server = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
        print('Bluetooth Socket Created')
        try:
            self.server.bind((host, port))
            print("Bluetooth Binding Completed")
        except:
            print("Bluetooth Binding Failed")

    def app_data():
        pass

    def device_thread():
        self.server.listen(7)
        while self.run:
            c, a = self.server.accept()
            self.client_list.append(c)
            self.address_list.append(a)
            # one thread for each connected device
            self.read_thread_list.append(device_thread(c))
            self.read_thread_list[len(read_thread_list)-1].start()
            print("New client: ", a)
