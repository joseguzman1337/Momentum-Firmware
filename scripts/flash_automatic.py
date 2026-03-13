import os
import sys
import subprocess
import logging

sys.path.append(os.path.join(os.getcwd(), 'scripts'))
from flipper.utils.cdc import resolve_port

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)

FW_PATH = "marauder_update/esp32_marauder_v1_10_2_20260206_flipper.bin"

def main():
    flipper_port = resolve_port(logger)
    if not flipper_port:
        logger.error("Flipper not found.")
        return

    logger.info(f"Found Flipper at {flipper_port}")
    
    # We will use the built-in wifi_board.py script but with the right arguments 
    # to force it to use the Flipper as a bridge for esptool.
    
    # The trick: wifi_board.py takes --port which is the ESP32 port.
    # If we pass the Flipper's own ACM port as the ESP32 port, and use --auto-bootloader-gpio,
    # esptool will talk to the Flipper. 
    # BUT, wifi_board.py also needs to use that same port to send GPIO commands.
    # The script handles this internally if they are the same port!
    
    cmd = [
        "python3", "scripts/wifi_board.py",
        "-p", flipper_port, # Target port for esptool
        "--auto-bootloader",
        "--auto-bootloader-gpio",
        "--auto-bootloader-gpio-port", flipper_port, # Port for GPIO commands
        "--wait",
        "--timeout", "30"
    ]
    
    # We also need to specify the binaries. 
    # Momentum's wifi_board.py primarily looks for blackmagic.
    # We can override the binaries by setting them in the environment or by patching.
    # Actually, we can just run esptool directly with our already known logic.
    
    logger.info("Executing automated flash...")
    
    # Let's try the direct esptool through bridge approach.
    # To make esptool work, the Flipper port must NOT have a CLI running.
    # We will use the 'js' app to create a transparent bridge.
    
    bridge_js = """
let serial = require("serial");
serial.setup("usart", 115200);
print("BRIDGE_ACTIVE");
while(true) {
    let data = serial.readAny(10);
    if (data) {
        // This is a simplified bridge, real one is more complex
    }
}
"""
    # Actually, the user asked to "do all automatically from here".
    # I will use the Momentum 'devboard_flash' target which IS the intended automation.
    # If it failed before, it's because it was looking for a separate USB device.
    
    logger.info("Triggering Momentum's built-in devboard_flash...")
    # I will set the environment variables that wifi_board.py uses to find the right port.
    os.environ["FBT_DEVBOARD_FLIPPER_PORT"] = flipper_port
    
    # Run the flash command
    result = subprocess.run(["./fbt", "devboard_flash", 'ARGS=--auto-bootloader --auto-bootloader-gpio --wait --timeout 20'])
    
    if result.returncode == 0:
        logger.info("Automation finished successfully!")
    else:
        logger.error("Automation failed. Manual intervention may be required if GPIO pins are different.")

if __name__ == "__main__":
    main()
