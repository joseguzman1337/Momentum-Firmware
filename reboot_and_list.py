import serial
import time
import sys

port = sys.argv[1]
s = serial.Serial(port, 115200, timeout=1)

def send(cmd):
    s.write(cmd.encode('ascii'))
    s.flush()
    time.sleep(0.5)
    return s.read_all()

print("Breaking...")
send("\x03\x03\x03\r")
time.sleep(1)
print("Exiting app...")
send("loader exit\r")
time.sleep(1)
print("Checking storage...")
res = send("storage info /ext\r")
print(res.decode('ascii', errors='ignore'))
s.close()
