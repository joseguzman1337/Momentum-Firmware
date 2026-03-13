import os
import sys
import time
import logging
import subprocess

sys.path.append(os.path.join(os.getcwd(), 'scripts'))
from flipper.utils.cdc import resolve_port
from flipper.storage import FlipperStorage

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)

def send_input(storage, key, duration="short"):
    storage.send(f"input send {key} {duration}\r\n")
    time.sleep(0.8)

def automate_fap_manual_flash(port):
    with FlipperStorage(port) as storage:
        logger.info("Initializing Flipper for manual flash...")
        storage.send('\x03\x03\x03') 
        time.sleep(0.5)
        storage.send('loader close\r\n')
        time.sleep(1)

        # 1. Start App
        logger.info("Opening [ESP] ESP Flasher...")
        storage.send('loader open "[ESP] ESP Flasher"\r\n')
        time.sleep(4) 
        
        # 2. Navigate to Manual Flash
        logger.info("Navigating to Manual Flash...")
        send_input(storage, "down")
        send_input(storage, "ok")
        time.sleep(1)
        
        # 3. Select 'Flash Firmware (0x10000)'
        logger.info("Selecting 'Flash Firmware (0x10000)'...")
        send_input(storage, "down") 
        send_input(storage, "down") 
        send_input(storage, "down") 
        send_input(storage, "ok")   
        time.sleep(2)
        
        # 4. Navigate to apps_data
        logger.info("Navigating File Browser...")
        for _ in range(15): send_input(storage, "up")
        for _ in range(5): send_input(storage, "down")
        send_input(storage, "ok") 
        
        # Navigate to esp_flasher
        for _ in range(15): send_input(storage, "up")
        for _ in range(5): send_input(storage, "down")
        send_input(storage, "ok") 
        
        # Navigate to Marauder
        for _ in range(15): send_input(storage, "up")
        for _ in range(5): send_input(storage, "down")
        send_input(storage, "ok") 
        
        # Select file
        for _ in range(10): send_input(storage, "up")
        send_input(storage, "ok") 
        
        # 5. Flash
        logger.info("Scrolling to FLASH button...")
        for _ in range(10): send_input(storage, "down")
        send_input(storage, "ok") 
        
        logger.info("MANUAL FLASH TRIGGERED. Waiting 4 minutes...")
        for i in range(240):
            if i % 10 == 0: sys.stdout.write(f" {i}s ")
            sys.stdout.write(".")
            sys.stdout.flush()
            time.sleep(1)
            
        logger.info("Done.")
        storage.send("power reboot\r\n")

if __name__ == "__main__":
    port = resolve_port(logger)
    if port:
        env = os.environ.copy()
        env["PYTHONPATH"] = os.path.join(os.getcwd(), "scripts")
        cmd_fmt = "from flipper.storage import FlipperStorage; from flipper.utils.cdc import resolve_port; import logging; logger = logging.getLogger(); port = resolve_port(logger); storage = FlipperStorage(port); storage.start(); storage.send_file('marauder_update/esp32_marauder_v1_10_2_20260206_flipper.bin', '{}')"
        for loc in ['/ext/apps_data/esp_flasher/assets/marauder/s2/esp32_marauder.flipper.bin', '/ext/apps_data/esp_flasher/Marauder/esp32_marauder.flipper.bin']:
            subprocess.run(["python3", "-c", cmd_fmt.format(loc)], env=env)
        automate_fap_manual_flash(port)
