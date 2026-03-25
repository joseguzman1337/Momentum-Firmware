#!/bin/bash
# Continuous WiFi Developer Board Monitoring and Auto-Flash Script
# This script continuously monitors for the WiFi board and flashes it automatically when detected

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}╔══════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║  WiFi Board Continuous Monitor & Auto-Flash            ║${NC}"
echo -e "${BLUE}╚══════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${YELLOW}This script will continuously monitor for the WiFi Developer Board${NC}"
echo -e "${YELLOW}and automatically flash it when detected in bootloader mode.${NC}"
echo ""
echo -e "${GREEN}✓${NC} Press Ctrl+C to stop monitoring"
echo ""
echo -e "${YELLOW}Waiting for WiFi Developer Board...${NC}"
echo ""

cd /home/d3c0d3r/x/Momentum-Firmware || exit 1

PYTHON_CMD="/home/d3c0d3r/.local/bin/python3"
if ! command -v "$PYTHON_CMD" &> /dev/null; then
    PYTHON_CMD="python3"
fi

ATTEMPT=0
LAST_CHECK=$(date +%s)

while true; do
    CURRENT_TIME=$(date +%s)
    
    # Check every 3 seconds
    if [ $((CURRENT_TIME - LAST_CHECK)) -ge 3 ]; then
        ATTEMPT=$((ATTEMPT + 1))
        
        # Check if ESP32-S2 device is present in bootloader mode
        if $PYTHON_CMD -c "import serial.tools.list_ports; ports = list(serial.tools.list_ports.grep('ESP32-S2')); exit(0 if len(ports) > 0 else 1)" 2>/dev/null; then
            echo ""
            echo -e "${GREEN}╔══════════════════════════════════════════════════════════╗${NC}"
            echo -e "${GREEN}║   WiFi Developer Board Detected! 🎉                     ║${NC}"
            echo -e "${GREEN}╚══════════════════════════════════════════════════════════╝${NC}"
            echo ""
            echo -e "${YELLOW}Starting flash procedure...${NC}"
            echo ""
            
            # Attempt flash
            if $PYTHON_CMD -m ufbt devboard_flash; then
                echo ""
                echo -e "${GREEN}╔══════════════════════════════════════════════════════════╗${NC}"
                echo -e "${GREEN}║   WiFi Developer Board Flashed Successfully! ✓          ║${NC}"
                echo -e "${GREEN}╚══════════════════════════════════════════════════════════╝${NC}"
                echo ""
                echo -e "${BLUE}Next steps:${NC}"
                echo "1. Press the RESET button on the WiFi board"
                echo "2. Disconnect and reconnect the USB-C cable"
                echo "3. The board is now ready to use!"
                echo ""
                exit 0
            else
                echo ""
                echo -e "${YELLOW}Flash attempt failed. Continuing to monitor...${NC}"
                echo ""
            fi
        fi
        
        # Print status every 10 attempts (30 seconds)
        if [ $((ATTEMPT % 10)) -eq 0 ]; then
            echo -e "${BLUE}[$(date '+%H:%M:%S')]${NC} Still waiting for WiFi board... (attempt $ATTEMPT)"
            echo "  ${YELLOW}→${NC} Make sure to hold BOOT and press RESET to enter bootloader mode"
        fi
        
        LAST_CHECK=$CURRENT_TIME
    fi
    
    sleep 1
done
