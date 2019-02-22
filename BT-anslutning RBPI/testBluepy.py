# Testa Bluepy på raspberryn
import bleio

# Create a Characteristic.
chara = bleio.Characteristic(bleio.UUID(0x2919), read=True, notify=True)

# Create a Service providing that one Characteristic.
serv = bleio.Service(bleio.UUID(0x180f), [chara])

# Create a peripheral and start it up.
periph = bleio.Peripheral([service])
periph.start_advertising()

while not periph.connected:
    # Wait for connection.
    pass

if periph.connected:
    print("Connected!!!")
