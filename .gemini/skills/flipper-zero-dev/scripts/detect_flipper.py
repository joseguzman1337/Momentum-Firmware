import logging
import sys
import os

# Add scripts to path so we can import flipper
sys.path.append(os.path.join(os.getcwd(), 'scripts'))

from flipper.utils.cdc import resolve_port
from flipper.storage import FlipperStorage

def main():
    logger = logging.getLogger('detect')
    handler = logging.StreamHandler(sys.stdout)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)

    print("Searching for Flipper Zero...")
    try:
        port = resolve_port(logger)
        if not port:
            print("No Flipper Zero detected.")
            return

        print(f"Detected Flipper on port: {port}")
        print("Connecting to get device info...")
        
        with FlipperStorage(port) as storage:
            # FlipperStorage.start() already sends device_info and waits for it
            # We can send it again to get the output if we want
            
            storage.send("device_info\r")
            # Skip the echo and command line
            storage.read.until("device_info\r\n")
            
            # Read until the next prompt
            info_data = storage.read.until(storage.CLI_PROMPT)
            print("\n--- Device Info ---")
            print(info_data.decode('ascii', 'ignore').strip())
            print("-------------------\n")

    except Exception as e:
        print(f"\nError during detection: {e}")

if __name__ == "__main__":
    main()