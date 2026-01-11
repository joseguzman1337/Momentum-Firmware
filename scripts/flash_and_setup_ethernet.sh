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

echo -e "${BLUE}╔══════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║   Momentum Firmware - Auto Flash & Ethernet Setup       ║${NC}"
echo -e "${BLUE}╚══════════════════════════════════════════════════════════╝${NC}"
echo ""

# Step 1: Build & Flash Firmware
echo -e "${YELLOW}[1/4] Building and flashing firmware...${NC}"
cd "$PROJECT_ROOT"
./fbt flash_usb_full

echo -e "${GREEN}[✓] Firmware flashed successfully${NC}"
echo ""

# Step 2: Enable USB Ethernet on Flipper
echo -e "${YELLOW}[2/4] Enabling USB Ethernet on Flipper...${NC}"
python3 "$SCRIPT_DIR/fbt_hooks/post_flash_usb_ethernet.py"

echo ""

# Step 3: Check if automation is installed
echo -e "${YELLOW}[3/4] Checking automation setup...${NC}"
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

# Step 4: Wait for USB Ethernet and enable internet
echo -e "${YELLOW}[4/4] Waiting for USB Ethernet interface...${NC}"
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
