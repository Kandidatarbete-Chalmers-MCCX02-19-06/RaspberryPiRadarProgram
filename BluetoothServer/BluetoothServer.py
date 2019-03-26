# Importing the Bluetooth Socket library
from typing import Any, Union

import bluetooth
import threading
import time
import math
import random

clientList = []         # list for each connected device, sockets
addressList = []        # list for mac-adresses from each connected device
readThreadList = []     # list for threads to recieve from each device
sinvalue = 0
run = True

host = ""
port = 1  # Raspberry Pi uses port 1 for Bluetooth Communication


def write_data_to_app(data,data_type):
    #print(data + ' ' + data_type)
    if data_type == 'pulse rate':
        string = ' PR ' + data + ' '
        #print(string)
        send_data(string)
    elif data_type == 'breath rate':
        string = ' BR ' + data + ' '
        #print(string)
        send_data(string)
    elif data_type == 'real time breath':
        string = ' RTB ' + data + ' '
        send_data(string)


def send_data(write):
    print('Send data: ' + write)
    for client in clientList:
        #print(addressList[clientList.index(client)])
        #print("Length " + str(len(clientList)))
        try:
            client.send(write.encode('utf-8'))      # write.encode('utf-8')
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

# Creaitng Socket Bluetooth RFCOMM communication
server = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
print('Bluetooth Socket Created')
try:
    server.bind((host, port))
    print("Bluetooth Binding Completed")
except:
    print("Bluetooth Binding Failed")


class ConnectDevicesThread(threading.Thread):
    def __init__(self,):
        super(ConnectDevicesThread, self).__init__()
        server.listen(7)

    def run(self):
        while run:
            c, a = server.accept()
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
                data = self.client.recv(1024)       # important to write self.client everywhere in the class/thread
                print(data.decode('utf-8'))
        except:
            self.client.close()
            print('remove client: ' + str(addressList[clientList.index(self.client)]))
            clientList.remove(self.client)


connectDevices = ConnectDevicesThread()
connectDevices.start()

for i in range(1,2000):
    time.sleep(1)
    while len(clientList) == 0:
        pass
    data = addData(sinvalue)
    #print('Write data: ' + data)
    data_pulse, data_breath = data.split(' ')
    write_data_to_app(data_pulse, 'pulse rate')
    write_data_to_app(data_breath, 'breath rate')
    sinvalue += 0.157

run = False
server.close()
