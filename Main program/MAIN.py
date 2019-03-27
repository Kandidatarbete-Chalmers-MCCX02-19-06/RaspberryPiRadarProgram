import time
import threading
import numpy as np
import queue

#import Radar
import Class_Thread
#import Filter

# Bluetooth:
import bluetooth
import math
import random

#bluetooth
import bluetoothThreads

# Main method for initiating and running radar measurements, signal processing and sending data through bluetooth to application.

# Variables bluetooth:
clientList = []         # list for each connected device, sockets
addressList = []        # list for mac-adresses from each connected device
readThreadList = []     # list for threads to recieve from each device
sinvalue = 0
run = True
host = ""
port = 1  # Raspberry Pi uses port 1 for Bluetooth Communication


def main():
    global sinvalue     # needed in order to use global variable

    # Creaitng Socket Bluetooth RFCOMM communication
    server = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
    print('Bluetooth Socket Created')
    try:
        server.bind((host, port))
        print("Bluetooth Binding Completed")
    except:
        print("Bluetooth Binding Failed")

    connectDevices = bluetoothThreads.ConnectDevicesThread()
    connectDevices.start()

    radar_queue = queue.Queue()
    interrupt_queue = queue.Queue()
    # heart_rate_queue = queue.Queue()
    # resp_rate_queue = queue.Queue()

    # radar = Radar.Radar(radar_queue, interrupt_queue)
    # radar.start()

    # radar = Class_Thread.Radar(radar_queue, interrupt_queue)
    # radar.get_data()

    # filter = Filter.Filter(radar_queue, interrupt_queue)
    # filter.start()


    # signalprocessing = Signalprocessing(radar_queue,heart_rate_queue,resp_rate_queue)
    # signalprocessing.start()

    # bluetooth = Bluetooth(heart_rate_queue,resp_rate_queue)
    # bluetooth.start()
    # bluetooth send data
    for i in range(1, 2000):
        time.sleep(1)
        while len(clientList) == 0:
            pass
        data = addData(sinvalue)
        # print('Write data: ' + data)
        data_pulse, data_breath = data.split(' ')
        write_data_to_app(data_pulse, 'heart rate')
        write_data_to_app(data_breath, 'breath rate')
        sinvalue += 0.157


    run = False
    server.close()


# Bluetooth functions
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
            client.send(write.encode('utf-8'))  # write.encode('utf-8')
        except:
            print("Error")

def addData(i):
    data = [70 + math.sin(i), 20 + math.sin(i+math.pi/4)]
    noise = random.random()
    data[0] += 5*(noise - 0.5)
    noise = random.random()
    data[1] += noise
    data[0] = round(data[0])
    data[1] = round(data[1])
    return str(data[0]) + ' ' + str(data[1])



if __name__ == "__main__":
    main()
