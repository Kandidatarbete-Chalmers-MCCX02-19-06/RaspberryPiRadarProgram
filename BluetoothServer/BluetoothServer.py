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

host = ""
port = 1  # Raspberry Pi uses port 1 for Bluetooth Communication

def addData(i):
    data = math.sin(i)
    noise = random.random()
    data += (noise - 0.5)
    return data

# Creaitng Socket Bluetooth RFCOMM communication
server = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
print('Bluetooth Socket Created')
try:
    server.bind((host, port))
    print("Bluetooth Binding Completed")
except:
    print("Bluetooth Binding Failed")


class ConnectDevicesThread(threading.Thread):       # thread for listening to and accepting incoming connections
    def __init__(self,):
        super(ConnectDevicesThread, self).__init__()
        server.listen(7)

    def run(self):
        while True:
            c, a = server.accept()
            clientList.append(c)
            addressList.append(a)
            readThreadList.append(ReadDeviceThread(c))       # one thread for each connected device
            readThreadList[len(readThreadList)-1].start()
            # print("Client:", c)


class ReadDeviceThread(threading.Thread):       # thread for reading messages from data
    client = None
    def __init__(self, client):
        self.client = client
        super(ReadDeviceThread, self).__init__()

    def run(self):
        try:
            while True:
                data = self.client.recv(1024)       # important to write self.client everywhere in the class/thread
                print(data.decode('utf-8'))
        except:
            pass


connectDevices = ConnectDevicesThread()
connectDevices.start()

for i in range(1,100):
    time.sleep(1)
    while len(clientList) == 0:
        pass
    #write = 'String from Raspberry Pi after received message' + str(i)
    write = addData(sinvalue)
    print(write)
    # print(write.encode('utf-8'))
    for client in clientList:
        print(addressList[clientList.index(client)])
        print("Length " + str(len(clientList)))
        try:
            client.send(write.encode('utf-8'))
        except:
            # Closing the client and server connection
            client.close()
            print('remove : ' + str(addressList[clientList.index(client)]))
            clientList.remove(client)
    sinvalue += 0.157

server.close()
