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
    
    with FlipperStorage(port) as storage:
        print("Releasing Devboard Reset...")
        storage.send("gpio mode PB2 1\r\n")
        storage.read.until(storage.CLI_PROMPT)
        storage.send("gpio set PB2 1\r\n")
        storage.read.until(storage.CLI_PROMPT)
        
        storage.send("gpio mode PC3 1\r\n")
        storage.read.until(storage.CLI_PROMPT)
        storage.send("gpio set PC3 1\r\n")
        storage.read.until(storage.CLI_PROMPT)
        print("Done. Waiting for USB discovery...")

if __name__ == "__main__":
    main()
