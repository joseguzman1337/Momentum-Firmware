import serial
import time
import sys

port = "/dev/cu.usbmodemflip_Asch1rp1"
s = serial.Serial(port, 115200, timeout=1)

def send(cmd):
    s.write(cmd.encode('ascii'))
    s.flush()
    time.sleep(0.5)
    return s.read_all()

print("Initial Stat:")
print(send("loader close\r").decode('ascii', errors='ignore'))
print("Sending Back keys...")
for _ in range(5):
    send("input key back press\r")
    send("input key back release\r")
print("Stat after Back:")
print(send("loader close\r").decode('ascii', errors='ignore'))
print("Sending Exit...")
print(send("loader exit\r").decode('ascii', errors='ignore'))
print("Waiting...")
time.sleep(1)
print("Final Stat:")
print(send("loader close\r").decode('ascii', errors='ignore'))
s.close()
