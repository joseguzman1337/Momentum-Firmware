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

print("Help system:")
print(send("system ?\r").decode('ascii', errors='ignore'))
print("Help power:")
print(send("power ?\r").decode('ascii', errors='ignore'))
s.close()
