import queue
import time
import threading
import bluetooth
import math
import random
import socket
import subprocess       # for Raspberry Pi shutdown
import os


class BluetoothServer:
    run = True  # Argument for shuting down all loops at the same time with input from one device.

    def __init__(self, list_of_variables_for_threads):
        # List of all variables from main to class.
        self.list_of_variables_for_threads = list_of_variables_for_threads
        # Bluetooth variables
        self.client_list = []         # list for each connected device, sockets
        self.address_list = []        # list for mac-adresses from each connected device
        # self.read_thread_list = []     # list for threads to recieve from each device
        self.host = ""
        self.port = 1
        self.client = None
        # Setup server for bluetooth communication
        self.server = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
        self.server.setblocking(0)  # Makes server.accept() non-blocking, used for "poweroff"
        # TEMP: Data from radar used to make sure data can be accepted between threads
        # Queue from radar class to test if queue communication work
        self.HR_final_queue = list_of_variables_for_threads["HR_final_queue"]
        self.RR_filtered_queue = list_of_variables_for_threads["RR_filtered_queue"]
        self.run_measurement = list_of_variables_for_threads["run_measurement"]
        print('Bluetooth Socket Created')
        try:
            self.server.bind((self.host, self.port))
            print("Bluetooth Binding Completed")
        except:
            print("Bluetooth Binding Failed")

        # Can be accessed from main-program to wait for it to close by .join()
        self.connect_device_thread = threading.Thread(
            target=self.connect_device)  # Starts thread which accepts new devices
        self.connect_device_thread.start()

    def app_data(self):  # The main loop which takes data from processing and sends data to all clients
        while self.list_of_variables_for_threads["go"]:
            time.sleep(1)
            while len(self.client_list) == 0:
                continue
            self.schmitt_to_app()
            self.real_time_breating_to_app()
            # data = self.add_data(d)  # TEMP: Makes random data for testing of communication
            # data_pulse, data_breath = data.split(' ')  # Splits data in pulse and heart rate
            # self.write_data_to_app(data_pulse, 'heart rate')  # Sends pulse to app
            # gitself.write_data_to_app(data_breath, 'breath rate')  # Sends heart rate to app

    def schmitt_to_app(self):
        try:
            # TEMP: Takes data from Schmitt trigger
            schmitt_data = self.HR_final_queue.get(timeout=0.2)
            schmitt_data = ' RR ' + schmitt_data + ' '
            self.send_data(schmitt_data)
        except:
            pass

    def real_time_breating_to_app(self):
        try:
            # TEMP: Takes data from Schmitt trigger
            real_time_breating_to_app = self.HR_final_queue.get(timeout=0.2)
            real_time_breating_to_app = ' RTB ' + real_time_breating_to_app + ' '
            self.send_data(real_time_breating_to_app)
        except:
            pass

    def connect_device(self):
        os.system("echo 'power on\nquit' | bluetoothctl")  # Startup for bluetooth on rpi
        thread_list = []  # List which adds devices
        self.server.listen(7)  # Amount of devices that can simultaniously recive data.
        while self.list_of_variables_for_threads["go"]:
            # Loop which takes listens for a new device, adds it to our list
            # and starts a new thread for listening on input from device
            try:
                c, a = self.server.accept()
            except:
                if self.run == False:
                    break
                #print("Still accepting new phones" + str(error))
                continue
            self.client_list.append(c)
            self.address_list.append(a)
            # one thread for each connected device
            thread_list.append(threading.Thread(target=self.read_device))
            thread_list[-1].start()
            print(thread_list[-1].getName())
            print(thread_list[-1].isAlive())
            print("New client: ", a)

        print("Out of while True in connect device")
        # Gracefully close all device threads
        for thread in thread_list:
            print(str(thread.getName()) + str(thread.isAlive()))
            thread.join()
            print(str(thread.getName()) + " is closed")
        print("End of connect_device thread")

    def read_device(self):
        c = self.client_list[-1]  # Takes last added device and connects it.
        print(c)
        print(self.address_list[-1])
        try:
            while self.list_of_variables_for_threads["go"]:
                data = c.recv(1024)  # Input argument from device
                data = data.decode('utf-8')
                data = data.strip()
                print(data)
                # When device sends "poweroff" initiate shutdown by setting run to false, removing all clients and closing all threads.
                if data == 'poweroff':
                    print("Shutdown starting")
                    try:
                        self.run = False
                        self.list_of_variables_for_threads["go"] = []
                        print("run= " + str(self.run))
                        for client in self.client_list:
                            print('try to remove client ' +
                                  str(self.address_list[self.client_list.index(client)]))
                            client.close()
                            print('remove client ' +
                                  str(self.address_list[self.client_list.index(client)]))
                        self.server.close()
                        print("server is now closed")
                        os.system("echo 'power off\nquit' | bluetoothctl")
                    except Exception as error:
                        print("exception in for-loop in read_device: " + str(error))

                elif data == 'startMeasure':
                    self.run_measurement.append(c)
                    self.list_of_variables_for_threads["run_measurement"] = self.run_measurement
                    print("Device added")

                elif data == 'stopMeasure':
                    if c in self.run_measurement:
                        self.run_measurement.remove(c)
                        self.list_of_variables_for_threads["run_measurement"] = self.run_measurement
                        print("Device removed")

        except Exception as error:
            print("last exception read_device: " + str(error))
            c.close()
            print('remove client: ' + str(self.address_list[self.client_list.index(c)]))
            if c in self.run_measurement:
                self.run_measurement.remove(c)
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
        for client in self.client_list:  # Send the same data to all clients connected
            try:
                client.send(write.encode('utf-8'))      # write.encode('utf-8')
            except Exception as error:
                print("Error send_data" + str(error))

    def add_data(self, i):  # TEMP: Make data somewhat random.
        data = [70 + math.sin(i), 20 + math.sin(i+math.pi/4)]
        noise = random.random()
        data[0] += 5*(noise - 0.5)
        noise = random.random()
        data[1] += noise
        data[0] = round(data[0])
        data[1] = round(data[1])
        return str(data[0]) + ' ' + str(data[1])

    # def get_data_from_queue(self):
    #     self.send_to_app_queue.put(self.add_data(1))
    #     return self.send_to_app_queue.get()

    @staticmethod  # Test to send run variable to other threads, does not work yet.
    def get_run(self):
        return self.run
