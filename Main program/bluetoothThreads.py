import bluetooth
import threading

class ConnectDevicesThread(threading.Thread):
    def __init__(self):
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
                if data.decode('utf-8') == 'poweroff':
                    # TODO Erik: Power off python program and Raspberry Pi
                    pass
        except:
            self.client.close()
            print('remove client: ' + str(addressList[clientList.index(self.client)]))
            clientList.remove(self.client)

