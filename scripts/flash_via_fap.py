import os
import sys
import time
import subprocess
import logging

sys.path.append(os.path.join(os.getcwd(), 'scripts'))
from flipper.utils.cdc import resolve_port
from flipper.storage import FlipperStorage

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)

def wait_for_prompt(storage):
    # Empty the buffer until prompt
    storage.read.until(storage.CLI_PROMPT)

def send_cli_cmd(storage, cmd, wait=True):
    r = chr(13)
    n = chr(10)
    storage.send(cmd + r + n)
    if wait:
        wait_for_prompt(storage)

def automate_fap_flashing(port):
    with FlipperStorage(port) as storage:
        logger.info("Killing any currently running apps...")
        storage.send(chr(13) + chr(10))
        time.sleep(0.1)
        storage.send('\x03') # Ctrl+C to get to a fresh prompt if needed
        time.sleep(0.5)
        
        # We don't want an exception here if loader isn't running
        try:
            send_cli_cmd(storage, "loader close")
        except:
            pass
        time.sleep(1)

        logger.info("Opening [ESP] ESP Flasher...")
        # Start the app. FAP names with spaces need quotes.
        send_cli_cmd(storage, 'loader open "[ESP] ESP Flasher"')
        
        # Give the app time to boot and render the main menu
        time.sleep(2)
        
        # 1. Main Menu: "Quick Flash" is the first option, so we just press OK
        logger.info("Selecting 'Quick Flash'...")
        send_cli_cmd(storage, "input send ok short", wait=False)
        time.sleep(1)
        
        # 2. Board Selection: "Flipper WiFi Devboard" is the first option, press OK
        logger.info("Selecting 'Flipper WiFi Devboard'...")
        send_cli_cmd(storage, "input send ok short", wait=False)
        time.sleep(1)
        
        # 3. Firmware Selection: "Marauder (has Evil Portal)" is the first option, press OK
        logger.info("Selecting 'Marauder' and starting flash...")
        send_cli_cmd(storage, "input send ok short", wait=False)
        
        # The flash process takes a while. We can just monitor the Flipper screen 
        # or wait a sufficient amount of time. The Flipper will beep or show "Success!"
        logger.info("Flash triggered! Waiting 60 seconds for completion...")
        
        # Print dots while waiting
        for i in range(60):
            sys.stdout.write('.')
            sys.stdout.flush()
            time.sleep(1)
            
        print("")
        logger.info("Flashing should be complete. Closing ESP Flasher app...")
        
        # Press back a few times to exit the app
        send_cli_cmd(storage, "input send back short", wait=False)
        time.sleep(0.5)
        send_cli_cmd(storage, "input send back short", wait=False)
        time.sleep(0.5)
        send_cli_cmd(storage, "input send back short", wait=False)
        
        # Just to be sure, force close
        try:
            send_cli_cmd(storage, "loader close")
        except:
            pass
            
        logger.info("Done! The devboard is updated and rebooting.")

def main():
    logger.info("Automating ESP32 Marauder update using Flipper Zero UI...")
    
    port = resolve_port(logger)
    if not port:
        logger.error("Could not find Flipper Zero.")
        sys.exit(1)
        
    logger.info(f"Connected to Flipper at {port}")
    automate_fap_flashing(port)

if __name__ == "__main__":
    main()
