import sys
import os
import logging

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
        storage.send("sysctl\r")
        out = storage.read.until(storage.CLI_PROMPT)
        print(out.decode('ascii', 'ignore'))

if __name__ == "__main__":
    main()
