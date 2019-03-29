import queue
import time
import threading
import bluetooth
import math
import random


class bluetooth_app:
    def __init__(self, send_to_app_queue):
        # Bluetooth variables
        self.client_list = []         # list for each connected device, sockets
        self.address_list = []        # list for mac-adresses from each connected device
        self.read_thread_list = []     # list for threads to recieve from each device
        self.run = True
        self.send_to_app_queue = send_to_app_queue
        self.host = ""
        self.port = 1
        self.client = None
        self.server = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
        print('Bluetooth Socket Created')
        try:
            self.server.bind((self.host, self.port))
            print("Bluetooth Binding Completed")
        except:
            print("Bluetooth Binding Failed")

    def app_data(self):
        connect_device_thread = threading.Thread(target=self.connect_device)
        connect_device_thread.start()

        for i in range(1, 2000):
            time.sleep(1)
            while len(self.client_list) == 0:
                pass
            data = self.add_data(1)
            # data = self.get_data_from_queue()
            # print('Write data: ' + data)
            data_pulse, data_breath = data.split(' ')
            self.write_data_to_app(data_pulse, 'heart rate')
            self.write_data_to_app(data_breath, 'breath rate')
            # sinvalue += 0.157
        self.server.close()

    def connect_device(self):  # Does not work properly
        self.server.listen(7)
        while self.run:
            c, a = self.server.accept()
            self.client_list.append(c)
            self.address_list.append(a)
            # one thread for each connected device
            # self.read_thread_list.append([c, a])
            # self.thread = threading.Thread(target=self.read_device, args=(c))
            self.read_thread_list.append(threading.Thread(name="device {}".format(
                len(self.client_list)), target=self.read_device, args=(c)))
            self.read_thread_list[-1].start()
            print("New client: ", a)

    def read_device(self, client):
        try:
            while self.run:
                self.data = self.client.recv(1024)
                print(self.data.decode('utf-8'))
                if self.data.decode('utf-8') == 'poweroff':
                    # TODO Erik: Power off python program and Raspberry Pi
                    pass
        except:  # never gets here
            self.client.close()
            print('remove client: ' + str(self.address_list[self.client_list.index(self.client)]))
            self.client_list.remove(self.client)

    def write_data_to_app(self, data, data_type):
        # print(data + ' ' + data_type)
        if data_type == 'heart rate':
            string = ' HR ' + data + ' '
            # print(string)
            self.send_data(string)
        elif data_type == 'breath rate':
            string = ' BR ' + data + ' '
            # print(string)
            self.send_data(string)
        elif data_type == 'real time breath':
            string = ' RTB ' + data + ' '
            self.send_data(string)

    def send_data(self, write):
        print('Send data: ' + write)
        for client in self.client_list:
            # print(addressList[clientList.index(client)])
            # print("Length " + str(len(clientList)))
            try:
                client.send(write.encode('utf-8'))      # write.encode('utf-8')
            except:
                print("Error")

    def add_data(self, i):
        data = [70 + math.sin(i), 20 + math.sin(i+math.pi/4)]
        noise = random.random()
        data[0] += 5*(noise - 0.5)
        noise = random.random()
        data[1] += noise
        data[0] = round(data[0])
        data[1] = round(data[1])
        return str(data[0]) + ' ' + str(data[1])

    def get_data_from_queue(self):
        self.send_to_app_queue.put(self.add_data(1))
        return self.send_to_app_queue.get()
