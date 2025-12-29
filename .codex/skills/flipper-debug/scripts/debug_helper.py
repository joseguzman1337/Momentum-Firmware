#!/usr/bin/env python3
"""
Flipper Zero Debug Helper
Connects to Flipper via serial and provides debugging utilities
"""

import serial
import sys
import time
import argparse

def connect_flipper(port="/dev/tty.usbmodemflip_*"):
    """Connect to Flipper Zero via serial"""
    try:
        ser = serial.Serial(port, 230400, timeout=1)
        return ser
    except Exception as e:
        print(f"Failed to connect: {e}")
        return None

def send_command(ser, command):
    """Send command to Flipper CLI"""
    ser.write(f"{command}\r\n".encode())
    time.sleep(0.1)
    response = ser.read_all().decode()
    return response

def debug_memory(ser):
    """Check memory usage"""
    print("=== Memory Debug ===")
    print(send_command(ser, "free"))

def debug_processes(ser):
    """List running processes"""
    print("=== Process Debug ===")
    print(send_command(ser, "ps"))

def debug_logs(ser):
    """Show system logs"""
    print("=== System Logs ===")
    print(send_command(ser, "log"))

def main():
    parser = argparse.ArgumentParser(description="Flipper Zero Debug Helper")
    parser.add_argument("--port", default="/dev/tty.usbmodemflip_*", help="Serial port")
    parser.add_argument("--memory", action="store_true", help="Check memory usage")
    parser.add_argument("--processes", action="store_true", help="List processes")
    parser.add_argument("--logs", action="store_true", help="Show logs")
    
    args = parser.parse_args()
    
    ser = connect_flipper(args.port)
    if not ser:
        sys.exit(1)
    
    if args.memory:
        debug_memory(ser)
    if args.processes:
        debug_processes(ser)
    if args.logs:
        debug_logs(ser)
    
    if not any([args.memory, args.processes, args.logs]):
        print("No debug option specified. Use --help for options.")
    
    ser.close()

if __name__ == "__main__":
    main()