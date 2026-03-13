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

GITHUB_API = "https://api.github.com/repos/justcallmekoko/ESP32Marauder/releases/latest"
DL_DIR = "marauder_update"

def get_latest_firmware_url():
    logger.info("Fetching latest release from GitHub...")
    response = requests.get(GITHUB_API)
    response.raise_for_status()
    data = response.json()
    
    version = data.get("tag_name", "unknown")
    logger.info(f"Latest version found: {version}")
    
    assets = data.get("assets", [])
    firmware_url = None
    
    for asset in assets:
        name = asset["name"]
        if name.startswith("esp32_marauder_v") and name.endswith("_flipper.bin"):
            firmware_url = asset["browser_download_url"]
            break

    if not firmware_url:
        raise Exception("Could not find the '_flipper.bin' firmware in the latest release.")
            
    return version, firmware_url

def download_file(url, filepath):
    logger.info(f"Downloading {os.path.basename(filepath)}...")
    response = requests.get(url, stream=True)
    response.raise_for_status()
    with open(filepath, 'wb') as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)
    logger.info(f"Saved to {filepath}")

def enter_bootloader(port):
    logger.info("Putting WiFi Devboard into bootloader mode via Flipper GPIO...")
    r = chr(13)
    n = chr(10)
    
    with FlipperStorage(port) as storage:
        storage.send("gpio mode PB2 1" + r + n)
        storage.read.until(storage.CLI_PROMPT)
        storage.send("gpio mode PC3 1" + r + n)
        storage.read.until(storage.CLI_PROMPT)
        
        # BOOT low, RESET low
        storage.send("gpio set PC3 0" + r + n)
        storage.read.until(storage.CLI_PROMPT)
        storage.send("gpio set PB2 0" + r + n)
        storage.read.until(storage.CLI_PROMPT)
        time.sleep(0.5)
        
        # RESET high (while BOOT is still low)
        storage.send("gpio set PB2 1" + r + n)
        storage.read.until(storage.CLI_PROMPT)
        time.sleep(0.5)
        
        # BOOT high
        storage.send("gpio set PC3 1" + r + n)
        storage.read.until(storage.CLI_PROMPT)
        
        logger.info("GPIO sequence complete. Waiting for ESP32-S2 to enumerate via USB...")
        time.sleep(5)

def find_esp32_port():
    import serial.tools.list_ports
    logger.info("Scanning for connected USB serial ports...")
    
    for port in serial.tools.list_ports.comports():
        logger.info(f" - Found: {port.device} (VID: {port.vid}, PID: {port.pid}, Desc: {port.description})")
        if port.vid == 0x303A or "ESP32" in str(port.description):
            return port.device
    return None

def flash_firmware(esp_port, flipper_bin_path):
    logger.info("Ensuring esptool is installed...")
    subprocess.run([sys.executable, "-m", "pip", "install", "esptool", "--quiet"], check=True)
    
    bootloader_path = "applications/external/esp_flasher/resources/apps_data/esp_flasher/assets/marauder/s2/esp32_marauder.ino.bootloader.bin"
    partition_path = "applications/external/esp_flasher/resources/apps_data/esp_flasher/assets/marauder/esp32_marauder.ino.partitions.bin"
    boot_app0_path = "applications/external/esp_flasher/resources/apps_data/esp_flasher/assets/marauder/boot_app0.bin"

    esptool_cmd = [
        sys.executable, "-m", "esptool",
        "--port", esp_port,
        "--baud", "460800", 
        "--before", "default_reset", 
        "--after", "hard_reset",
        "--chip", "esp32s2",
        "write_flash",
        "0x1000", bootloader_path,
        "0x8000", partition_path,
        "0xE000", boot_app0_path,
        "0x10000", flipper_bin_path
    ]
    
    logger.info(f"Executing: {' '.join(esptool_cmd)}")
    
    result = subprocess.run(esptool_cmd, capture_output=True, text=True)
    if result.returncode == 0:
        logger.info("Flash completed successfully!")
        print(result.stdout)
    else:
        logger.error("Flash failed!")
        print(result.stdout)
        print(result.stderr)
        sys.exit(1)

def main():
    if not os.path.exists(DL_DIR):
        os.makedirs(DL_DIR)
        
    try:
        version, fw_url = get_latest_firmware_url()
        
        filename = fw_url.split("/")[-1]
        fw_path = os.path.join(DL_DIR, filename)
        if not os.path.exists(fw_path):
            download_file(fw_url, fw_path)
        else:
            logger.info(f"File {filename} already exists, skipping download.")
        
        flipper_port = resolve_port(logger)
        if not flipper_port:
            logger.error("Could not find connected Flipper Zero.")
            sys.exit(1)
        logger.info(f"Found Flipper at {flipper_port}")
        
        enter_bootloader(flipper_port)
        
        esp_port = find_esp32_port()
        if not esp_port:
            logger.error("Could not find ESP32 Devboard natively via USB.")
            logger.info("Attempting to flash via Flipper serial bridge...")
            # If the devboard is not showing up as its own USB device, we fallback 
            # to using the Flipper's bridge. But standard esptool might struggle with the CLI prompt.
            # We will use the `scripts/wifi_board.py` wrapper which knows how to handle the Flipper bridge!
            logger.info("Delegating to standard Momentum flasher...")
            subprocess.run(["python3", "scripts/wifi_board.py", "--wait", "--timeout", "10", "--auto-bootloader", "--auto-bootloader-gpio"], check=True)
            sys.exit(0)
            
        logger.info(f"Found ESP32 Devboard natively at {esp_port}")
        flash_firmware(esp_port, fw_path)
        
        logger.info("All done! The devboard should reboot into the updated firmware.")
        
    except Exception as e:
        logger.error(f"Update process failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
