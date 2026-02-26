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

def send_input(storage, key):
    storage.send(f"input send {key} short\r\n")
    time.sleep(0.8)

def automate_full_flash(port):
    with FlipperStorage(port) as storage:
        logger.info("Starting robust UI automation...")
        storage.send('loader open "[ESP] ESP Flasher"\r\n')
        time.sleep(3)
        
        logger.info("Navigating to Quick Flash...")
        # Make sure we are at top
        send_input(storage, "up")
        send_input(storage, "ok")   # Enter Quick Flash
        time.sleep(1)
        send_input(storage, "ok")   # Select Flipper WiFi Devboard
        time.sleep(1)
        send_input(storage, "ok")   # Select Marauder
        
        logger.info("FLASH TRIGGERED. Waiting 3 minutes...")
        for i in range(180):
            if i % 10 == 0: sys.stdout.write(f" {i}s ")
            sys.stdout.write(".")
            sys.stdout.flush()
            time.sleep(1)
        
        logger.info("Done. Rebooting.")
        storage.send("power reboot\r\n")

if __name__ == "__main__":
    port = resolve_port(logger)
    if port:
        env = os.environ.copy()
        env["PYTHONPATH"] = os.path.join(os.getcwd(), "scripts")
        # Direct call to storage operations
        subprocess.run(["python3", "-c", "from flipper.storage import FlipperStorage; from flipper.utils.cdc import resolve_port; import logging; logger = logging.getLogger(); port = resolve_port(logger); storage = FlipperStorage(port); storage.start(); storage.remove('/ext/apps_data/esp_flasher/assets/marauder/s2/esp32_marauder.flipper.bin'); storage.send_file('marauder_update/esp32_marauder_v1_10_2_20260206_flipper.bin', '/ext/apps_data/esp_flasher/assets/marauder/s2/esp32_marauder.flipper.bin')"], env=env, check=True)
        automate_full_flash(port)
