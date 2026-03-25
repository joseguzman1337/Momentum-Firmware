#!/bin/bash
# Flipper Zero Auto USB Ethernet Setup
# Automatically detects Flipper and enables USB Ethernet mode

set -e

USB_DEV="$1"
ACTION="${2:-start}"
LOG_FILE="/var/log/flipper-ethernet.log"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" | tee -a "$LOG_FILE"
}

find_flipper_serial() {
    # Find Flipper Zero serial port
    for port in /dev/ttyACM* /dev/serial/by-id/*Flipper*; do
        if [ -e "$port" ]; then
            echo "$port"
            return 0
        fi
    done
    return 1
}

enable_usb_ethernet_on_flipper() {
    local SERIAL_PORT="$1"

    log "Enabling USB Ethernet on Flipper via $SERIAL_PORT"

    # Use FlipperSerial library if available
    if [ -d "$SCRIPT_DIR/../tools/fz" ]; then
        python3 - "$SERIAL_PORT" <<'PYTHON'
import sys
import time
sys.path.insert(0, sys.argv[0].replace('flipper-auto-ethernet-setup.sh', '../tools/fz'))

try:
    from flipperzero import FlipperZero

    port = sys.argv[1]
    flipper = FlipperZero(port=port)
    flipper.connect()

    # Send CLI commands to enable USB Ethernet
    flipper.cli_send("storage read /int/.system/usb.mode")
    time.sleep(0.5)

    # Set USB mode to Ethernet
    flipper.cli_send("storage write /int/.system/usb.mode usb_eth")
    time.sleep(0.5)

    # Reboot to apply
    flipper.cli_send("power reboot")

    flipper.disconnect()
    print("USB Ethernet enabled on Flipper")

except Exception as e:
    print(f"Error: {e}", file=sys.stderr)
    # Fallback to raw serial commands
    import serial
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
    print(f"Response: {response}")

    # Reboot
    ser.write(b'power reboot\r\n')
    time.sleep(0.5)

    ser.close()
    print("USB Ethernet enabled (fallback mode)")
PYTHON
    else
        # Fallback using stty/screen
        log "WARNING: FlipperSerial not found, using fallback method"

        # Configure serial port
        stty -F "$SERIAL_PORT" 115200 cs8 -cstopb -parenb raw

        # Send commands
        {
            sleep 0.5
            echo ""
            sleep 0.2
            echo "storage write /int/.system/usb.mode usb_eth"
            sleep 0.5
            echo "power reboot"
            sleep 0.5
        } > "$SERIAL_PORT"
    fi

    log "USB Ethernet enable command sent, waiting for reboot..."
    sleep 5
}

wait_for_usb_ethernet() {
    local MAX_WAIT=30
    local COUNT=0

    log "Waiting for USB Ethernet interface to appear..."

    while [ $COUNT -lt $MAX_WAIT ]; do
        # Check for Flipper USB Ethernet interface
        for iface in /sys/class/net/enx*; do
            if [ -d "$iface" ]; then
                IFACE_NAME=$(basename "$iface")
                # Verify it's Flipper (VID:0483 PID:5740)
                if grep -q "0483:5740" "/sys/class/net/$IFACE_NAME/device/uevent" 2>/dev/null; then
                    log "Found Flipper USB Ethernet: $IFACE_NAME"
                    echo "$IFACE_NAME"
                    return 0
                fi
            fi
        done

        sleep 1
        COUNT=$((COUNT + 1))
    done

    log "ERROR: USB Ethernet interface not found after ${MAX_WAIT}s"
    return 1
}

case "$ACTION" in
    start)
        log "Flipper Zero detected on USB: $USB_DEV"

        # Find serial port
        SERIAL_PORT=$(find_flipper_serial)
        if [ -z "$SERIAL_PORT" ]; then
            log "ERROR: Could not find Flipper serial port"
            exit 1
        fi

        log "Found Flipper serial: $SERIAL_PORT"

        # Enable USB Ethernet on Flipper
        enable_usb_ethernet_on_flipper "$SERIAL_PORT" || true

        # Wait for USB Ethernet interface
        ETH_IFACE=$(wait_for_usb_ethernet)
        if [ -n "$ETH_IFACE" ]; then
            # Enable internet sharing
            "$SCRIPT_DIR/flipper-internet-share.sh" "$ETH_IFACE" start
        fi
        ;;

    stop)
        log "Flipper Zero disconnected: $USB_DEV"
        # Cleanup handled by udev rule
        ;;

    *)
        echo "Usage: $0 <usb_device> {start|stop}"
        exit 1
        ;;
esac

exit 0
