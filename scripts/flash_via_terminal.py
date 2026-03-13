import os
import sys
import time
import requests
import subprocess
import logging

sys.path.append(os.path.join(os.getcwd(), 'scripts'))
from flipper.utils.cdc import resolve_port
from flipper.storage import FlipperStorage

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)

def enter_bootloader_and_start_bridge(port):
    logger.info("Connecting to Flipper to toggle GPIO and start bridge...")
    r = chr(13)
    n = chr(10)
    
    with FlipperStorage(port) as storage:
        # Exit any running app first just in case
        storage.send(r + n)
        time.sleep(0.1)
        storage.send('\x03') # Ctrl+C
        time.sleep(0.5)
        storage.send("loader close" + r + n)
        time.sleep(1)

        # Toggle GPIO to Bootloader
        logger.info("Toggling GPIO pins...")
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
        logger.info("ESP32-S2 is in bootloader mode.")

        # Launch UART Terminal to create the bridge
        logger.info("Launching UART Terminal to bridge USB and USART...")
        storage.send('loader open "UART Terminal"' + r + n)
        time.sleep(2) # Give it time to start
        
    logger.info("Bridge should be active now.")

def flash_firmware(port):
    logger.info("Running esptool to flash firmware...")
    fw_path = "marauder_update/esp32_marauder_v1_10_2_20260206_flipper.bin"
    bootloader_path = "applications/external/esp_flasher/resources/apps_data/esp_flasher/assets/marauder/s2/esp32_marauder.ino.bootloader.bin"
    partition_path = "applications/external/esp_flasher/resources/apps_data/esp_flasher/assets/marauder/esp32_marauder.ino.partitions.bin"
    boot_app0_path = "applications/external/esp_flasher/resources/apps_data/esp_flasher/assets/marauder/boot_app0.bin"

    esptool_cmd = [
        sys.executable, "-m", "esptool",
        "--port", port,
        "--baud", "115200", 
        "--before", "no_reset", 
        "--after", "no_reset",
        "--chip", "esp32s2",
        "write_flash",
        "0x1000", bootloader_path,
        "0x8000", partition_path,
        "0xE000", boot_app0_path,
        "0x10000", fw_path
    ]
    
    logger.info(f"Executing: {' '.join(esptool_cmd)}")
    
    # We must stream output so we can see what's happening
    process = subprocess.Popen(esptool_cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    for line in process.stdout:
        print(line, end="")
    process.wait()
    
    if process.returncode == 0:
        logger.info("Flash completed successfully!")
        return True
    else:
        logger.error("Flash failed!")
        return False

def main():
    port = resolve_port(logger)
    if not port:
        logger.error("Flipper not found.")
        sys.exit(1)
        
    enter_bootloader_and_start_bridge(port)
    success = flash_firmware(port)
    
    if not success:
        sys.exit(1)

if __name__ == "__main__":
    main()
