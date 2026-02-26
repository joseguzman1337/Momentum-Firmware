#!/usr/bin/env python3
import sys
import os
import time
import argparse
import logging

sys.path.append(os.path.join(os.getcwd(), 'scripts'))
from flipper.utils.cdc import resolve_port
from flipper.storage import FlipperStorage

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)

def main():
    parser = argparse.ArgumentParser(description="Marauder Automation Bridge")
    parser.add_argument("cmd", help="Command to run", nargs="?", default="info")
    parser.add_argument("params", help="Additional parameters", nargs="*", default=[])
    
    args = parser.parse_args()
    full_command = " ".join([args.cmd] + args.params).strip()
    
    port = resolve_port(logger)
    if not port:
        print("Error: Flipper Zero not detected.")
        sys.exit(1)
        
    js_payload = f"""
let serial = require("serial");
serial.setup("usart", 115200);
serial.write("{full_command}\\r\\n");
for (let i = 0; i < 60; i++) {{
    let data = serial.readAny(500);
    if (data) print(data);
}}
serial.end();
"""
    
    with FlipperStorage(port) as storage:
        logger.info("Cleaning Flipper state...")
        storage.send('\x03\x03')
        time.sleep(0.5)
        storage.send("loader close\r\n")
        time.sleep(1)
        storage.read.until(storage.CLI_PROMPT)
        
        target_path = "/ext/marauder_auto.js"
        
        logger.info("Transferring automation logic...")
        with open("tmp_marauder.js", "w") as f:
            f.write(js_payload)
        
        storage.start()
        storage.send_file("tmp_marauder.js", target_path)
        os.remove("tmp_marauder.js")
        
        logger.info(f"Executing: {full_command}")
        storage.send(f"js {target_path}\r\n")
        
        # Capture the output
        output = storage.read.until(storage.CLI_PROMPT).decode('ascii', 'ignore')
        
        # Clean up and print
        capture = False
        for line in output.splitlines():
            if "Running script" in line:
                capture = True
                continue
            if "Script done" in line:
                break
            if capture:
                print(line)
        
        storage.remove(target_path)
        logger.info("Automation complete.")

if __name__ == "__main__":
    main()
