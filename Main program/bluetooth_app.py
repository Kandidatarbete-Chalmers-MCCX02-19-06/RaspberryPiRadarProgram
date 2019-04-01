import queue
import time
import threading
import bluetooth
import math
import random
import socket
import subprocess       # for Raspberry Pi shutdown
import os


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
        self.server.setblocking(0)
        self.from_radar_queue = from_radar_queue
        self.timeout = time.time() + 10
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

    def connect_device(self):  # Does not work properly
        thread_list = []
        self.server.listen(7)
        while self.run:
            try:
                c, a = self.server.accept()
            except:
                if self.run == False:
                    break
                continue
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

        print("Out of while True in connect device")
        # print("in exception for connect_device")
        for thread in thread_list:
            print(str(thread.getName()) + str(thread.isAlive()))
            thread.join()
            print(str(thread.getName()) + " is closed")

        # print("Out of while True in Connect_device")
        # for client in self.client_list:
        #     print('try to remove client ' + str(self.address_list[self.client_list.index(client)]))
        #     client.shutdown()
        #     client.close()
        #     print('remove client ' + str(self.address_list[self.client_list.index(client)]))

        # self.server.close()
        # print("server is now closed")

        # for thread in thread_list:
        #     print(thread.getName() + thread.isAlive())
        #     thread.join()
        #     print(thread.getName() + " is closed")

    def read_device(self):
        c = self.client_list[-1]
        print(c)
        print(self.address_list[-1])
        try:
            while self.run:
                try:
                    data = c.recv(1024)
                    data = data.decode('utf-8')
                    data = data.strip()
                    print(data)
                except:
                    time.sleep(1)
                    if self.run == False:
                        break
                    continue

                if data == 'poweroff':
                    print("Shutdown starting")
                    # subprocess.call(["sudo", "shutdown", "-h", "now"])
                    # TODO Erik: Power off python program and Raspberry Pi
                    try:
                        self.run = False
                        # print("Out of while True in Connect_device")
                        for client in self.client_list:
                            print('try to remove client ' +
                                  str(self.address_list[self.client_list.index(client)]))
                            # client.shutdown()
                            client.close()
                            print('remove client ' +
                                  str(self.address_list[self.client_list.index(client)]))
                            time.sleep(1)

                        # self.server.shutdown(self.server.SHUT_RDWR)
                        self.server.close()
                        # self.server.shutdown(1)
                        print("server is now closed")
                        #subprocess.call(["echo", "-e", "power on\nquit", "|", "bluetoothctl"])
                        #subprocess.call(["bluetoothctl"])
                        #subprocess.call(["power off"])
                        #subprocess.call(["quit"])
                        #subprocess.call(["echo", "-e", "\'power off\nquit\'", "|", "bluetoothctl"])
                        os.system("'echo -e' 'power off\nquit' | bluetoothctl")
                        # print("run= " + str(self.run))
                        # for client in self.client_list:     # closes and removes clients from list to cause exceptions and thereby closing the thread
                        #     print("Try client.close")
                        #     print("Length client_list " + str(len(self.client_list)))
                        #     # try calling <client.shutdown()> before because close does release resources allocated for client but does not close it straight away.
                        #     client.shutdown()
                        #     client.close()
                        #     print('remove client: ' +
                        #           str(self.address_list[self.client_list.index(client)]))
                        #     # self.client_list.remove(c)
                        # self.server.close()
                    except Exception as error:
                        print("exception in for-loop in read_device: " + str(error))

        except Exception as error:
            print("last exception read_device: " + str(error))
            c.close()
            print('remove client: ' + str(self.address_list[self.client_list.index(c)]))
            self.client_list.remove(c)
            self._is_running = False

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
                print("Error send_data")

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
