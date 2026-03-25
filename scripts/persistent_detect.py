#!/usr/bin/env python3
import os
import time
import sys
import select
import traceback

PORT = "/dev/ttyACM0"
PAIRS = [
    ("PC3", "PB2"), 
    ("PC3", "PB3"), 
    ("PA7", "PA6"), 
    ("PA7", "PA4")
]

def write_cmd_fast(fd, cmd):
    try:
        cmd_bytes = (cmd + "\r").encode('ascii')
        os.write(fd, cmd_bytes)
        # Don't wait for response, just blast
        time.sleep(0.05) 
    except Exception:
        raise

def wait_for_port():
    print("Waiting for Flipper USB connection...")
    while True:
        if os.path.exists(PORT):
            # Wait a split second for udev to settle permissions
            time.sleep(0.5) 
            return
        time.sleep(0.5)

def attempt_sequence():
    fd = -1
    try:
        print(f"Opening {PORT}...")
        fd = os.open(PORT, os.O_RDWR | os.O_NOCTTY | os.O_NONBLOCK)
        
        # Clear buffer
        # read_response(fd) # Skip reading to be fast
        
        # Ensure CLI
        os.write(fd, b"\x03\r\n")
        time.sleep(0.1)

        print("Executing Rapid Fire GPIO Toggle...")
        
        for boot, reset in PAIRS:
            # print(f"  > {boot}/{reset}")
            write_cmd_fast(fd, f"gpio mode {boot} 1")
            write_cmd_fast(fd, f"gpio mode {reset} 1")
            write_cmd_fast(fd, f"gpio set {boot} 0")
            write_cmd_fast(fd, f"gpio set {reset} 0")
            time.sleep(0.1) 
            write_cmd_fast(fd, f"gpio set {reset} 1")
            write_cmd_fast(fd, f"gpio set {boot} 1")
            
        print("Sequence complete. Checking for Devboard...")
        return True

    except Exception as e:
        print(f"Connection lost during sequence: {e}")
        return False
    finally:
        if fd >= 0:
            try:
                os.close(fd)
            except:
                pass

def check_devboard():
    if os.path.exists("/sys/bus/usb/devices"):
        for device in os.listdir("/sys/bus/usb/devices"):
            try:
                vid_path = f"/sys/bus/usb/devices/{device}/idVendor"
                if os.path.exists(vid_path):
                    with open(vid_path, "r") as f:
                        vid = f.read().strip()
                    if vid == "303a":
                        return device
            except:
                pass
    return None

def main():
    print("Starting Persistent Detection Loop...")
    print("This script will catch the Flipper whenever it connects and try to reset the Devboard.")
    print("Press Ctrl+C to stop.\n")
    
    while True:
        wait_for_port()
        
        # Try to execute
        if attempt_sequence():
            # Check for result
            start_check = time.time()
            while time.time() - start_check < 5:
                dev = check_devboard()
                if dev:
                    print(f"\nSUCCESS! Devboard detected at {dev}!")
                    return 0
                time.sleep(0.5)
            print("Devboard not detected yet.")
        
        # If Flipper disconnects, loop will catch it again
        time.sleep(1)

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\nExiting.")
