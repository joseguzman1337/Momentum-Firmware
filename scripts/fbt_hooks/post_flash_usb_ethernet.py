#!/usr/bin/env python3
"""
FBT Post-Flash Hook - Auto USB Ethernet Setup
Automatically enables USB Ethernet after flashing firmware
"""

import os
import sys
import time
import subprocess
from pathlib import Path

# Add FlipperSerial to path
TOOLS_DIR = Path(__file__).parent.parent.parent / "tools" / "fz"
if TOOLS_DIR.exists():
    sys.path.insert(0, str(TOOLS_DIR))

def log(message):
    """Print colored log message"""
    print(f"\033[1;36m[AUTO-ETHERNET]\033[0m {message}")

def find_flipper_port():
    """Find Flipper Zero serial port"""
    import glob

    # Try common patterns
    patterns = [
        "/dev/ttyACM*",
        "/dev/serial/by-id/*Flipper*",
        "/dev/cu.usbmodem*",  # macOS
    ]

    for pattern in patterns:
        ports = glob.glob(pattern)
        if ports:
            return ports[0]

    return None

def enable_usb_ethernet_flipper(port):
    """Enable USB Ethernet on Flipper Zero via serial"""
    log(f"Enabling USB Ethernet on Flipper via {port}")

    try:
        # Try using FlipperSerial library
        from flipperzero import FlipperZero

        flipper = FlipperZero(port=port)
        flipper.connect()

        # Check current USB mode
        log("Checking current USB mode...")
        flipper.cli_send("storage read /int/.system/usb.mode")
        time.sleep(0.5)

        # Enable USB Ethernet
        log("Setting USB mode to Ethernet...")
        flipper.cli_send("storage write /int/.system/usb.mode usb_eth")
        time.sleep(0.5)

        # Reboot to apply
        log("Rebooting Flipper to apply changes...")
        flipper.cli_send("power reboot")

        flipper.disconnect()
        log("✓ USB Ethernet enabled successfully")
        return True

    except ImportError:
        log("FlipperSerial not available, using fallback...")
        return enable_usb_ethernet_fallback(port)
    except Exception as e:
        log(f"Error: {e}")
        return enable_usb_ethernet_fallback(port)

def enable_usb_ethernet_fallback(port):
    """Fallback method using pyserial"""
    try:
        import serial

        log(f"Using pyserial fallback for {port}")
        ser = serial.Serial(port, 115200, timeout=2)
        time.sleep(1)

        # Clear buffer
        ser.read(ser.in_waiting or 1024)

        # Send commands
        ser.write(b'\r\n')
        time.sleep(0.2)

        ser.write(b'storage write /int/.system/usb.mode usb_eth\r\n')
        time.sleep(0.5)
        response = ser.read(ser.in_waiting or 1024).decode('utf-8', errors='ignore')
        log(f"Response: {response.strip()}")

        # Reboot
        ser.write(b'power reboot\r\n')
        time.sleep(0.5)

        ser.close()
        log("✓ USB Ethernet enabled (fallback mode)")
        return True

    except Exception as e:
        log(f"Fallback failed: {e}")
        return False

def trigger_internet_sharing():
    """Trigger internet sharing setup (if installed)"""
    log("Waiting for Flipper to reboot and reconnect...")
    time.sleep(10)

    # Check if automation is installed
    if os.path.exists("/usr/local/bin/flipper-internet-share.sh"):
        log("Automation detected - Internet sharing will start automatically")
        return True
    else:
        log("⚠ Automation not installed")
        log("  Run: sudo ./scripts/install-flipper-auto-ethernet.sh")
        return False

def main():
    """Main hook function"""
    log("Post-flash USB Ethernet setup started")

    # Wait for Flipper to finish booting
    log("Waiting for Flipper to finish booting...")
    time.sleep(3)

    # Find Flipper port
    port = find_flipper_port()
    if not port:
        log("⚠ Could not find Flipper serial port")
        log("  Flipper may not be connected or still booting")
        return 1

    log(f"Found Flipper on {port}")

    # Enable USB Ethernet
    if enable_usb_ethernet_flipper(port):
        trigger_internet_sharing()
        log("✓ All done! USB Ethernet should be ready")
        return 0
    else:
        log("⚠ Failed to enable USB Ethernet automatically")
        log("  You can enable it manually on Flipper:")
        log("    Settings → System → USB → USB Ethernet")
        return 1

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        log("Interrupted by user")
        sys.exit(130)
    except Exception as e:
        log(f"Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
