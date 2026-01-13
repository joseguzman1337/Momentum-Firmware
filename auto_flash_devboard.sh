#!/bin/bash
# Automated WiFi Developer Board Flash Script
# This script monitors for the WiFi board in bootloader mode and flashes it automatically

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${YELLOW}╔══════════════════════════════════════════════════════════╗${NC}"
echo -e "${YELLOW}║  WiFi Developer Board Automated Flash Script           ║${NC}"
echo -e "${YELLOW}╚══════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${YELLOW}Instructions:${NC}"
echo "1. Connect WiFi Dev Board via USB-C cable to your computer"
echo "2. Hold the BOOT button on the WiFi board"
echo "3. Press and release the RESET button (while holding BOOT)"
echo "4. Release the BOOT button"
echo ""
echo -e "${GREEN}The script will automatically detect and flash the board...${NC}"
echo ""

# Change to firmware directory
cd /home/d3c0d3r/x/Momentum-Firmware || exit 1

# Use ufbt if available, otherwise use fbt
if command -v /home/d3c0d3r/.local/bin/python3 &> /dev/null; then
    PYTHON_CMD="/home/d3c0d3r/.local/bin/python3"
elif command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
else
    echo -e "${RED}Error: Python 3 not found${NC}"
    exit 1
fi

# Try using fbt first to use local patched scripts
echo -e "${YELLOW}Attempting flash with local fbt (patched)...${NC}"
if ./fbt devboard_flash ARGS="--wait --timeout 180 --auto-bootloader"; then
    echo -e "${GREEN}╔══════════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║   WiFi Developer Board Flashed Successfully! ✓          ║${NC}"
    echo -e "${GREEN}╚══════════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo "Next steps:"
    echo "1. Press the RESET button on the WiFi board to reboot it"
    echo "2. Reconnect USB-C cable"
    echo "3. The board is now ready to use!"
    exit 0
fi

# Fallback to ufbt
echo -e "${YELLOW}Fallback: Attempting flash with ufbt...${NC}"
if $PYTHON_CMD -m ufbt devboard_flash --wait --timeout 180 --auto-bootloader; then
    echo -e "${GREEN}╔══════════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║   WiFi Developer Board Flashed Successfully! ✓          ║${NC}"
    echo -e "${GREEN}╚══════════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo "Next steps:"
    echo "1. Press the RESET button on the WiFi board to reboot it"
    echo "2. Reconnect USB-C cable"
    echo "3. The board is now ready to use!"
    exit 0
fi

echo -e "${RED}╔══════════════════════════════════════════════════════════╗${NC}"
echo -e "${RED}║   Flash Failed - Board Not Detected                     ║${NC}"
echo -e "${RED}╚══════════════════════════════════════════════════════════╝${NC}"
echo ""
echo "Troubleshooting:"
echo "1. Make sure the WiFi board is connected via USB-C"
echo "2. Verify you held BOOT and pressed RESET correctly"
echo "3. Try a different USB port or cable"
echo "4. Check that udev rules are installed (already done)"
exit 1
