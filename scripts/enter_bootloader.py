import sys
import os
import logging
import time

sys.path.append(os.path.join(os.getcwd(), 'scripts'))

from flipper.utils.cdc import resolve_port
from flipper.storage import FlipperStorage

def main():
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger()
    port = resolve_port(logger)
    if not port:
        print("No Flipper detected")
        return
    
    r = chr(13)
    n = chr(10)
    
    with FlipperStorage(port) as storage:
        print("Entering Bootloader Sequence...")
        storage.send("gpio mode PB2 1" + r + n)
        storage.read.until(storage.CLI_PROMPT)
        storage.send("gpio mode PC3 1" + r + n)
        storage.read.until(storage.CLI_PROMPT)
        
        storage.send("gpio set PC3 0" + r + n)
        storage.read.until(storage.CLI_PROMPT)
        storage.send("gpio set PB2 0" + r + n)
        storage.read.until(storage.CLI_PROMPT)
        time.sleep(0.5)
        
        storage.send("gpio set PB2 1" + r + n)
        storage.read.until(storage.CLI_PROMPT)
        time.sleep(0.5)
        
        storage.send("gpio set PC3 1" + r + n)
        storage.read.until(storage.CLI_PROMPT)
        print("Done. Checking for USB discovery...")

if __name__ == "__main__":
    main()
