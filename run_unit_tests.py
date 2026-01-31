import sys
import os
from pathlib import Path

# Add scripts to path to import FlipperStorage
sys.path.append(str(Path(__file__).parent / "scripts"))
from flipper.storage import FlipperStorage

def main():
    port = "/dev/cu.usbmodemflip_Asch1rp1"
    print(f"Connecting to Flipper on {port}...")
    
    try:
        with FlipperStorage(port) as storage:
            print("Connected. Running unit_tests...")
            # We don't use send_and_wait_prompt because unit_tests might take a long time
            # and produce lots of output.
            storage.send("unit_tests\r")
            
            # Read until we see the prompt again
            while True:
                line = storage.read.until("\r\n", timeout_sec=60).decode("ascii", "ignore")
                print(line)
                if ">: " in line:
                    break
                    
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()