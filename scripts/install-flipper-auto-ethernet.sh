#!/bin/bash
# Flipper Zero Auto USB Ethernet - Installation Script
# Installs udev rules, systemd services, and automation scripts

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}╔══════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║   Flipper Zero Auto USB Ethernet Installer              ║${NC}"
echo -e "${GREEN}╚══════════════════════════════════════════════════════════╝${NC}"
echo ""

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo -e "${RED}[ERROR] Please run as root (use sudo)${NC}"
    exit 1
fi

echo -e "${YELLOW}[*] Installing automation scripts...${NC}"

# Install scripts
install -m 755 "$SCRIPT_DIR/flipper-internet-share.sh" /usr/local/bin/
install -m 755 "$SCRIPT_DIR/flipper-auto-ethernet-setup.sh" /usr/local/bin/

echo -e "${GREEN}[✓] Scripts installed to /usr/local/bin/${NC}"

# Install udev rules
echo -e "${YELLOW}[*] Installing udev rules...${NC}"
install -m 644 "$SCRIPT_DIR/99-flipper-auto-ethernet.rules" /etc/udev/rules.d/

echo -e "${GREEN}[✓] Udev rules installed${NC}"

# Install systemd service
echo -e "${YELLOW}[*] Installing systemd service...${NC}"
install -m 644 "$SCRIPT_DIR/flipper-ethernet@.service" /etc/systemd/system/

# Reload systemd
systemctl daemon-reload

echo -e "${GREEN}[✓] Systemd service installed${NC}"

# Reload udev rules
echo -e "${YELLOW}[*] Reloading udev rules...${NC}"
udevadm control --reload-rules
udevadm trigger

echo -e "${GREEN}[✓] Udev rules reloaded${NC}"

# Check for required packages
echo -e "${YELLOW}[*] Checking dependencies...${NC}"

MISSING_DEPS=()

if ! command -v iptables &> /dev/null; then
    MISSING_DEPS+=("iptables")
fi

if ! command -v python3 &> /dev/null; then
    MISSING_DEPS+=("python3")
fi

if [ ${#MISSING_DEPS[@]} -gt 0 ]; then
    echo -e "${YELLOW}[!] Missing dependencies: ${MISSING_DEPS[*]}${NC}"
    echo -e "${YELLOW}[!] Install with: sudo apt install ${MISSING_DEPS[*]}${NC}"
else
    echo -e "${GREEN}[✓] All dependencies satisfied${NC}"
fi

# Optional: Install dnsmasq for DHCP
if ! command -v dnsmasq &> /dev/null; then
    echo -e "${YELLOW}[!] Optional: Install dnsmasq for automatic IP assignment${NC}"
    echo -e "${YELLOW}    sudo apt install dnsmasq${NC}"
fi

# Create log directory
mkdir -p /var/log
touch /var/log/flipper-ethernet.log
chmod 644 /var/log/flipper-ethernet.log

echo -e "${GREEN}[✓] Log file created${NC}"

# Install Python dependencies if FlipperSerial is available
if [ -d "$SCRIPT_DIR/../tools/fz" ]; then
    echo -e "${YELLOW}[*] Installing Python FlipperSerial dependencies...${NC}"
    python3 -m pip install pyserial --quiet || echo -e "${YELLOW}[!] Could not install pyserial${NC}"
fi

echo ""
echo -e "${GREEN}╔══════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║   Installation Complete!                                ║${NC}"
echo -e "${GREEN}╚══════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${GREEN}What happens now:${NC}"
echo -e "  1. ${YELLOW}Plug in your Flipper Zero${NC}"
echo -e "  2. ${GREEN}Automation detects it and enables USB Ethernet${NC}"
echo -e "  3. ${GREEN}Internet sharing is automatically configured${NC}"
echo -e "  4. ${GREEN}Flipper can download ESP32 firmware over HTTP${NC}"
echo ""
echo -e "${YELLOW}Manual commands (if needed):${NC}"
echo -e "  • Enable manually: ${GREEN}sudo flipper-internet-share.sh <interface> start${NC}"
echo -e "  • Check status:    ${GREEN}sudo flipper-internet-share.sh <interface> status${NC}"
echo -e "  • View logs:       ${GREEN}tail -f /var/log/flipper-ethernet.log${NC}"
echo ""
echo -e "${YELLOW}To uninstall:${NC}"
echo -e "  ${RED}sudo rm /etc/udev/rules.d/99-flipper-auto-ethernet.rules${NC}"
echo -e "  ${RED}sudo rm /etc/systemd/system/flipper-ethernet@.service${NC}"
echo -e "  ${RED}sudo rm /usr/local/bin/flipper-{internet-share,auto-ethernet-setup}.sh${NC}"
echo ""
echo -e "${GREEN}Enjoy automatic USB Ethernet with your Flipper Zero! 🐬${NC}"
echo ""

exit 0
