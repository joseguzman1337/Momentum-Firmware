#!/usr/bin/env python3
import os
import time
import sys
import select

PORT = "/dev/ttyACM0"
PAIRS = [
    ("PC3", "PB2"), # Default for V1
    ("PC3", "PB3"), # Alternative
    ("PA7", "PA6"), # Some ESP32-C3 modules?
    ("PA7", "PA4"), # Another variant
]

def read_response(fd):
    out = b""
    while True:
        r, _, _ = select.select([fd], [], [], 0.1)
        if fd in r:
            chunk = os.read(fd, 1024)
            if not chunk: break
            out += chunk
        else:
            break
    return out

def write_cmd(fd, cmd):
    cmd_bytes = (cmd + "\r").encode('ascii')
    # print(f"Sending: {cmd.strip()}")
    os.write(fd, cmd_bytes)
    time.sleep(0.05)
    return read_response(fd)

def check_for_device():
    if os.path.exists("/sys/bus/usb/devices"):
        for device in os.listdir("/sys/bus/usb/devices"):
            try:
                vid_path = f"/sys/bus/usb/devices/{device}/idVendor"
                if os.path.exists(vid_path):
                    with open(vid_path, "r") as f:
                        vid = f.read().strip()
                    if vid == "303a": # Espressif
                        return device
            except:
                pass
    return None

def main():
    print(f"Opening {PORT} in raw mode...")
    fd = -1
    try:
        fd = os.open(PORT, os.O_RDWR | os.O_NOCTTY | os.O_NONBLOCK)
    except Exception as e:
        print(f"Failed to open port: {e}")
        return 1

    try:
        # Clear buffer & Ensure CLI
        read_response(fd)
        print("Initializing CLI...")
        for _ in range(3):
            os.write(fd, b"\x03")
            time.sleep(0.1)
        
        resp = read_response(fd)
        if b">:" in resp:
            print("Flipper CLI prompt ready.")
        else:
            print("Warning: No prompt detected, proceeding anyway.")

        for boot_pin, reset_pin in PAIRS:
            print(f"\nTrying GPIO Pair: BOOT={boot_pin}, RESET={reset_pin}")
            
            # 1. Set pins to Output
            write_cmd(fd, f"gpio mode {boot_pin} 1")
            write_cmd(fd, f"gpio mode {reset_pin} 1")
            
            # 2. Hold BOOT (LOW)
            write_cmd(fd, f"gpio set {boot_pin} 0")
            time.sleep(0.1)
            
            # 3. Press RESET (LOW)
            write_cmd(fd, f"gpio set {reset_pin} 0")
            time.sleep(0.1)
            
            # 4. Release RESET (HIGH)
            write_cmd(fd, f"gpio set {reset_pin} 1")
            time.sleep(0.1)
            
            # 5. Release BOOT (HIGH)
            write_cmd(fd, f"gpio set {boot_pin} 1")
            
            print("  Sequence sent. Waiting for device...")
            
            # Wait 5 seconds
            start_wait = time.time()
            while time.time() - start_wait < 5:
                dev = check_for_device()
                if dev:
                    print(f"\nSUCCESS! Device found at {dev} using pair {boot_pin}/{reset_pin}")
                    os.close(fd)
                    return 0
                time.sleep(0.5)
                sys.stdout.write(".")
                sys.stdout.flush()
            print("\n  Not found.")

        print("\nAll pairs failed. Board not detected.")
        os.close(fd)
        return 1

    except Exception as e:
        print(f"Error: {e}")
        if fd >= 0: os.close(fd)
        return 1

if __name__ == "__main__":
    sys.exit(main())
