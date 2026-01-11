#!/bin/bash
# Momentum Firmware - Auto Flash & USB Ethernet Setup
# Builds, flashes firmware, and automatically sets up USB Ethernet

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[1;34m'
NC='\033[0m'

DEVBOARD_FLASH=0
DEVBOARD_CHANNEL="release"
DEVBOARD_TIMEOUT=180
DEVBOARD_AUTO_BOOTLOADER=1
DEVBOARD_AUTO_BOOTLOADER_PORT="auto"
SKIP_FLIPPER_FLASH=0
AUTO_FORMAT_EXT=0

usage() {
    echo "Usage: $0 [--devboard-flash] [--devboard-channel <release|dev|rc>] [--devboard-timeout <seconds>] [--devboard-auto-bootloader <on|off>] [--devboard-auto-bootloader-port <port>] [--skip-flipper-flash] [--auto-format-ext]"
}

reset_flipper_usb() {
    local dev
    dev=$(lsusb | awk '/0483:5740/ {print $2, $4}' | head -1 | awk '{gsub(":", "", $2); print $1 " " $2}')
    if [ -z "$dev" ]; then
        return 1
    fi
    local bus
    local devnum
    bus=$(echo "$dev" | awk '{print $1}')
    devnum=$(echo "$dev" | awk '{print $2}')
    local path="/dev/bus/usb/${bus}/${devnum}"
    if [ -x /usr/bin/usbreset ]; then
        /usr/bin/usbreset "$path" >/dev/null 2>&1 && return 0
        sudo -n /usr/bin/usbreset "$path" >/dev/null 2>&1 && return 0
    fi
    return 1
}

MM_STOPPED=0
maybe_stop_modemmanager() {
    if command -v systemctl >/dev/null 2>&1; then
        if systemctl is-active --quiet ModemManager; then
            if sudo -n systemctl stop ModemManager >/dev/null 2>&1; then
                MM_STOPPED=1
            fi
        fi
    fi
}

maybe_start_modemmanager() {
    if [ "$MM_STOPPED" -eq 1 ] && command -v systemctl >/dev/null 2>&1; then
        sudo -n systemctl start ModemManager >/dev/null 2>&1 || true
    fi
}

trap maybe_start_modemmanager EXIT

while [ $# -gt 0 ]; do
    case "$1" in
        --devboard-flash)
            DEVBOARD_FLASH=1
            shift
            ;;
        --devboard-channel)
            DEVBOARD_CHANNEL="$2"
            shift 2
            ;;
        --devboard-timeout)
            DEVBOARD_TIMEOUT="$2"
            shift 2
            ;;
        --devboard-auto-bootloader)
            if [ "$2" = "off" ]; then
                DEVBOARD_AUTO_BOOTLOADER=0
            else
                DEVBOARD_AUTO_BOOTLOADER=1
            fi
            shift 2
            ;;
        --devboard-auto-bootloader-port)
            DEVBOARD_AUTO_BOOTLOADER_PORT="$2"
            shift 2
            ;;
        --skip-flipper-flash)
            SKIP_FLIPPER_FLASH=1
            shift
            ;;
        --auto-format-ext)
            AUTO_FORMAT_EXT=1
            shift
            ;;
        -h|--help)
            usage
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            usage
            exit 1
            ;;
    esac
done

echo -e "${BLUE}╔══════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║   Momentum Firmware - Auto Flash & Ethernet Setup       ║${NC}"
echo -e "${BLUE}╚══════════════════════════════════════════════════════════╝${NC}"
echo ""

TOTAL_STEPS=4
if [ "$DEVBOARD_FLASH" -eq 1 ]; then
    TOTAL_STEPS=5
fi

STEP=1

# Step 1: Build & Flash Firmware
echo -e "${YELLOW}[${STEP}/${TOTAL_STEPS}] Building and flashing firmware...${NC}"
cd "$PROJECT_ROOT"
if [ "$SKIP_FLIPPER_FLASH" -eq 1 ]; then
    echo -e "${YELLOW}[!] Skipping firmware flash (requested)${NC}"
else
    if [ "$AUTO_FORMAT_EXT" -eq 1 ]; then
        if ! timeout 20s python3 "$SCRIPT_DIR/ensure_flipper_ext.py" --wait --timeout 30 --format-if-missing; then
            echo -e "${YELLOW}[!] /ext check failed; continuing anyway${NC}"
        fi
    fi
    maybe_stop_modemmanager
    timeout 5s python3 "$SCRIPT_DIR/set_usb_mode.py" --mode usb_serial || true
    FLASH_ATTEMPTS=0
    attempt=0
    FLIPPER_PORTS=()
    if ls /dev/serial/by-id/*Flipper* >/dev/null 2>&1; then
        while IFS= read -r port; do
            FLIPPER_PORTS+=("$port")
        done < <(ls -1 /dev/serial/by-id/*Flipper*)
    fi
    if ls /dev/ttyACM* >/dev/null 2>&1; then
        while IFS= read -r port; do
            FLIPPER_PORTS+=("$port")
        done < <(ls -1 /dev/ttyACM*)
    fi
    if [ "${#FLIPPER_PORTS[@]}" -eq 0 ]; then
        FLIPPER_PORTS=("auto")
    fi
    while true; do
        attempt=$((attempt + 1))
        if [ "$FLASH_ATTEMPTS" -gt 0 ]; then
            echo -e "${YELLOW}    Flash attempt ${attempt}/${FLASH_ATTEMPTS}...${NC}"
        else
            echo -e "${YELLOW}    Flash attempt ${attempt} (retrying until success)...${NC}"
        fi

        timeout 5s python3 "$SCRIPT_DIR/set_usb_mode.py" --mode usb_serial || true
        for port in "${FLIPPER_PORTS[@]}"; do
            if FLIPPER_PATH="$port" FBT_FLIPPER_BAUD=115200 FBT_STORAGE_CHUNK_SIZE=1024 ./fbt flash_usb_full; then
                break 2
            fi
            if FLIPPER_PATH="$port" FBT_FLIPPER_BAUD=230400 FBT_STORAGE_CHUNK_SIZE=1024 ./fbt flash_usb_full; then
                break 2
            fi
        done
        reset_flipper_usb || true
        if [ "$FLASH_ATTEMPTS" -gt 0 ] && [ "$attempt" -ge "$FLASH_ATTEMPTS" ]; then
            exit 1
        fi
        sleep 3
    done
fi

echo -e "${GREEN}[✓] Firmware step complete${NC}"
echo ""

STEP=$((STEP + 1))

# Step 2: Enable USB Ethernet on Flipper
echo -e "${YELLOW}[${STEP}/${TOTAL_STEPS}] Enabling USB Ethernet on Flipper...${NC}"
python3 "$SCRIPT_DIR/fbt_hooks/post_flash_usb_ethernet.py"

echo ""

STEP=$((STEP + 1))

# Step 3: Check if automation is installed
echo -e "${YELLOW}[${STEP}/${TOTAL_STEPS}] Checking automation setup...${NC}"
if [ -f "/etc/udev/rules.d/99-flipper-auto-ethernet.rules" ]; then
    echo -e "${GREEN}[✓] Automation already installed${NC}"
else
    echo -e "${YELLOW}[!] Automation not installed${NC}"
    echo -e "${YELLOW}    Installing automation (requires sudo)...${NC}"

    if sudo "$SCRIPT_DIR/install-flipper-auto-ethernet.sh"; then
        echo -e "${GREEN}[✓] Automation installed successfully${NC}"
    else
        echo -e "${YELLOW}[!] Automation install failed${NC}"
        echo -e "${YELLOW}    You can install it later with:${NC}"
        echo -e "${YELLOW}    sudo $SCRIPT_DIR/install-flipper-auto-ethernet.sh${NC}"
    fi
fi

echo ""

STEP=$((STEP + 1))

# Step 4: Wait for USB Ethernet and enable internet
echo -e "${YELLOW}[${STEP}/${TOTAL_STEPS}] Waiting for USB Ethernet interface...${NC}"
MAX_WAIT=30
COUNT=0

while [ $COUNT -lt $MAX_WAIT ]; do
    # Look for Flipper USB Ethernet
    FLIPPER_ETH=$(ip link show | grep -o 'enx[0-9a-f]*' | head -1 || true)

    if [ -n "$FLIPPER_ETH" ]; then
        echo -e "${GREEN}[✓] Found Flipper USB Ethernet: $FLIPPER_ETH${NC}"

        # Check if automation handled it
        if ip addr show "$FLIPPER_ETH" | grep -q "10.42.0.1"; then
            echo -e "${GREEN}[✓] Internet sharing enabled automatically${NC}"
        else
            # Manual enable
            echo -e "${YELLOW}[!] Enabling internet sharing manually...${NC}"
            if [ -x "/usr/local/bin/flipper-internet-share.sh" ]; then
                sudo /usr/local/bin/flipper-internet-share.sh "$FLIPPER_ETH" start
            else
                sudo "$SCRIPT_DIR/enable_internet.sh"
            fi
        fi

        echo ""
        echo -e "${GREEN}╔══════════════════════════════════════════════════════════╗${NC}"
        echo -e "${GREEN}║   Setup Complete! 🎉                                    ║${NC}"
        echo -e "${GREEN}╚══════════════════════════════════════════════════════════╝${NC}"
        echo ""
        echo -e "${GREEN}Your Flipper Zero is ready with:${NC}"
        echo -e "  ✓ Latest Momentum firmware"
        echo -e "  ✓ USB Ethernet enabled"
        echo -e "  ✓ Internet connection shared"
        echo ""
        echo -e "${BLUE}Next steps:${NC}"
        echo -e "  1. On Flipper: Apps → GPIO → [ESP] ESP Flasher"
        echo -e "  2. Download ESP32 Marauder firmware (auto HTTP download)"
        echo -e "  3. Flash your WiFi module"
        echo ""
        echo -e "${YELLOW}Status:${NC}"
        ip addr show "$FLIPPER_ETH"
        echo ""

        if [ "$DEVBOARD_FLASH" -eq 1 ]; then
            STEP=$((STEP + 1))
            echo -e "${YELLOW}[${STEP}/${TOTAL_STEPS}] Flashing WiFi devboard via fbt...${NC}"
            echo -e "${YELLOW}    Put the WiFi board in bootloader mode (hold BOOT, tap RESET).${NC}"
            DEVBOARD_ARGS="-c $DEVBOARD_CHANNEL --wait --timeout $DEVBOARD_TIMEOUT"
            if [ "$DEVBOARD_AUTO_BOOTLOADER" -eq 1 ]; then
                DEVBOARD_ARGS="$DEVBOARD_ARGS --auto-bootloader --auto-bootloader-port $DEVBOARD_AUTO_BOOTLOADER_PORT"
            fi
            ./fbt devboard_flash ARGS="$DEVBOARD_ARGS"
            echo -e "${GREEN}[✓] WiFi devboard flashed${NC}"
            echo ""
        fi

        exit 0
    fi

    sleep 1
    COUNT=$((COUNT + 1))
    echo -n "."
done

echo ""
echo -e "${YELLOW}[!] USB Ethernet not detected after ${MAX_WAIT}s${NC}"
echo -e "${YELLOW}    Manual steps:${NC}"
echo -e "    1. On Flipper: Settings → System → USB → USB Ethernet"
echo -e "    2. Run: sudo $SCRIPT_DIR/enable_internet.sh"
echo ""

exit 1
