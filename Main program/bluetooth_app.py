import queue
import time
import threading
import bluetooth
import math
import random


class bluetooth_app:
    run = True

    def __init__(self, send_to_app_queue, from_radar_queue):
        # Bluetooth variables
        self.client_list = []         # list for each connected device, sockets
        self.address_list = []        # list for mac-adresses from each connected device
        self.read_thread_list = []     # list for threads to recieve from each device
        self.send_to_app_queue = send_to_app_queue
        self.host = ""
        self.port = 1
        self.client = None
        self.server = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
        self.from_radar_queue = from_radar_queue
        print('Bluetooth Socket Created')
        try:
            self.server.bind((self.host, self.port))
            print("Bluetooth Binding Completed")
        except:
            print("Bluetooth Binding Failed")

        # Can be accessed from main-program to wait for it to close by .join()
        self.connect_device_thread = threading.Thread(target=self.connect_device)
        self.connect_device_thread.start()

    def app_data(self):
        while self.run:
            # for i in range(1, 2000):
            time.sleep(1)
            while len(self.client_list) == 0:
                pass
            d = self.from_radar_queue.get()
            data = self.add_data(d)
            # data = self.get_data_from_queue()
            # print('Write data: ' + data)
            data_pulse, data_breath = data.split(' ')
            self.write_data_to_app(data_pulse, 'heart rate')
            self.write_data_to_app(data_breath, 'breath rate')
            # sinvalue += 0.157
        self.server.close()

    def connect_device(self):  # Does not work properly
        thread_list = []
        self.server.listen(7)
        while self.run:
            c, a = self.server.accept()
            self.client_list.append(c)
            self.address_list.append(a)
            # one thread for each connected device
            # self.read_thread_list.append([c, a])
            thread_list.append(threading.Thread(target=self.read_device))
            thread_list[-1].start()
            print(thread_list[-1].getName())
            print(thread_list[-1].isAlive())
            # self.read_thread_list.append(threading.Thread(target=self.read_device, args=(len(self.client_list)))
            # self.read_thread_list[-1].start()
            print("New client: ", a)

        for thread in thread_list:
            thread.join()
            print(thread.getName() + " is closed")

    def read_device(self):
        c = self.client_list[-1]
        print(c)
        print(self.address_list[-1])
        try:
            while self.run:
                data = c.recv(1024)
                print(data.decode('utf-8'))
                if data.decode('utf-8') == 'poweroff':
                    print("Shutdown starting")
                    # TODO Erik: Power off python program and Raspberry Pi
                    try:
                        self.run = False
                        print("run= " + str(self.run))
                        for client in self.client_list:     # closes and removes clients from list to cause exceptions and thereby closing the thread
                            client.close()
                            print('remove client: ' +
                                  str(self.address_list[self.client_list.index(client)]))
                            self.client_list.remove(c)
                    except:
                        print("exception in for-loop")

        except:
            c.close()
            print('remove client: ' + str(self.address_list[self.client_list.index(c)]))
            self.client_list.remove(c)

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

    @staticmethod
    def get_run(self):
        return self.run
