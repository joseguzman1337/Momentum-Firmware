#!/usr/bin/env python3
import sys
import os
import argparse
import time

# Mock pytz if not available
try:
    import pytz
except ImportError:
    import types
    pytz = types.ModuleType("pytz")
    pytz.timezone = lambda x: None
    sys.modules["pytz"] = pytz

# Add the FZ library path
FZ_LIB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "../tools/fz/lib/python"))
sys.path.insert(0, FZ_LIB_PATH)

try:
    from flipper_serial.flipper_serial import FlipperSerial
    from flipper_serial.common import SerialConfig
except ImportError as e:
    print(f"Error importing Flipper library: {e}")
    sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description="Flipper Zero Warp CLI")
    parser.add_argument("command", nargs="*", help="Command to send to Flipper")
    parser.add_argument("--port", default="/dev/ttyACM0", help="Serial port")
    parser.add_argument("--baud", type=int, default=115200, help="Baud rate")
    
    args = parser.parse_args()
    
    command = " ".join(args.command)
    if not command:
        print("Please provide a command to run.")
        return

    config = SerialConfig(
        port=args.port,
        baudrate=args.baud,
        timeout=2.0 # Increased timeout for reliability
    )
    
    # Override log dir to tmp
    config.log_dir = "/home/d3c0d3r/.gemini/tmp/a53b67593fe97a2ef8678b5165d459fe1a74d8f743586553e304159d27c703c0/logs"
    
    flipper = FlipperSerial(config)
    
    try:
        if flipper.connect():
            # Send command
            # The library sends \r\n automatically in send_command
            response = flipper.send_command(command, wait_time=0.5)
            print(response)
        else:
            print("Failed to connect to Flipper Zero.")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        flipper.close()

if __name__ == "__main__":
    main()