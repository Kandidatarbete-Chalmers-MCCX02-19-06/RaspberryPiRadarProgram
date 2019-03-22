# Importing the Bluetooth Socket library
import bluetooth
import threading
import time

clientList = []
addressList = []

host = ""
port = 1  # Raspberry Pi uses port 1 for Bluetooth Communication
# Creaitng Socket Bluetooth RFCOMM communication
server = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
print('Bluetooth Socket Created')
try:
    server.bind((host, port))
    print("Bluetooth Binding Completed")
except:
    print("Bluetooth Binding Failed")

# for i in range(1,2):
#server.listen(2)  # One connection at a time
# Server accepts the clients request and assigns a mac address.
#client, address = server.accept()
#print("Connected To", address)
#print("Client:", client)

# server.listen(2)  # One connection at a time
# Server accepts the clients request and assigns a mac address.
#client2, address2 = server.accept()
#print("Connected To", address2)
#print("Client:", client2)


class ConnectDevicesThread(threading.Thread):
    def __init__(self,):
        super(ConnectDevicesThread, self).__init__()
        server.listen(7)

    def run(self):
        while True:
            c, a = server.accept()
            clientList.append(c)
            addressList.append(a)
            print("Client:", c)


connectDevices = ConnectDevicesThread()
connectDevices.start()

for i in range(1,100):
    time.sleep(1)
    while len(clientList) == 0:
        pass
    write = 'String from Raspberry Pi after received message' + i
    print(write)
    # print(write.encode('utf-8'))
    for client in clientList:
        print(clientList.index(client))
        try:
            client.send(write.encode('utf-8'))
        except:
            # Closing the client and server connection
            client.close()
            clientList.remove(client)
            print('remove: '+client)


server.close()