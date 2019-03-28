from typing import Any, Union

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
# sinvalue = 0
run = True
test_queue = queue.Queue()
host = ""
# Raspberry Pi uses port 1 for Bluetooth Communication
#port = bluetooth.get_available_port(bluetooth.RFCOMM)
port = 2

# Queues:


def main():
    radar_queue = queue.Queue()
    interrupt_queue = queue.Queue()
    # heart_rate_queue = queue.Queue()
    # resp_rate_queue = queue.Queue()

    # radar = Radar.Radar(radar_queue, interrupt_queue)
    # radar.start()

    # Creaitng Socket Bluetooth RFCOMM communication
    server = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
    print('Bluetooth Socket Created')
    try:
        server.bind((host, port))
        print("Bluetooth Binding Completed")
    except:
        print("Bluetooth Binding Failed")

    connectDevices = ConnectDevicesThread(server)
    connectDevices.start()

    for i in range(1, 2000):
        time.sleep(1)
        while len(clientList) == 0:
            pass
        # data = addData(sinvalue)
        data = getDataFromQueue()
        # print('Write data: ' + data)
        data_pulse, data_breath = data.split(' ')
        write_data_to_app(data_pulse, 'heart rate')
        write_data_to_app(data_breath, 'breath rate')
        # sinvalue += 0.157

    interrupt_queue.put(1)
    server.close()

    # Bluetooth functions:


def write_data_to_app(data, data_type):
    # print(data + ' ' + data_type)
    if data_type == 'heart rate':
        string = ' HR ' + data + ' '
        # print(string)
        send_data(string)
    elif data_type == 'breath rate':
        string = ' BR ' + data + ' '
        # print(string)
        send_data(string)
    elif data_type == 'real time breath':
        string = ' RTB ' + data + ' '
        send_data(string)


def send_data(write):
    print('Send data: ' + write)
    for client in clientList:
        # print(addressList[clientList.index(client)])
        # print("Length " + str(len(clientList)))
        try:
            client.send(write.encode('utf-8'))      # write.encode('utf-8')
        except:
            print("Error")


def addData(i):
    data = [70 + math.sin(4*i), 20 + math.sin(i+math.pi/4)]
    noise = random.random()
    data[0] += 5*(noise - 0.5)
    noise = random.random()
    data[1] += noise
    data[0] = round(data[0])
    data[1] = round(data[1])
    return str(data[0]) + ' ' + str(data[1])


def getDataFromQueue():
    test_queue.put(addData(1))
    return test_queue.get()


# Bluetooth classes:
class ConnectDevicesThread(threading.Thread):
    def __init__(self, server):
        super(ConnectDevicesThread, self).__init__()
        self.server = server
        self.server.listen(7)

    def run(self):
        while run:
            c, a = self.server.accept()
            clientList.append(c)
            addressList.append(a)
            readThreadList.append(ReadDeviceThread(c))       # one thread for each connected device
            readThreadList[len(readThreadList)-1].start()
            print("New client: ", a)


class ReadDeviceThread(threading.Thread):
    client = None

    def __init__(self, client):
        self.client = client
        super(ReadDeviceThread, self).__init__()

    def run(self):
        try:
            while run:
                # important to write self.client everywhere in the class/thread
                data = self.client.recv(1024)
                print(data.decode('utf-8'))
                if data.decode('utf-8') == 'poweroff':
                    # TODO Erik: Power off python program and Raspberry Pi
                    pass
        except:
            self.client.close()
            print('remove client: ' + str(addressList[clientList.index(self.client)]))
            clientList.remove(self.client)


if __name__ == "__main__":
    main()
