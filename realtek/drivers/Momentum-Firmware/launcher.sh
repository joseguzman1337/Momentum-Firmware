#!/bin/bash

# RTL8814AU Quick Launcher
# Simple menu-driven interface for driver management

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

clear

echo -e "${CYAN}"
cat << "EOF"
╔═══════════════════════════════════════════════════════════════╗
║                                                               ║
║   ██████╗ ████████╗██╗      █████╗  █████╗ ██╗  ██╗ █████╗  ║
║   ██╔══██╗╚══██╔══╝██║     ██╔══██╗██╔══██╗██║  ██║██╔══██╗ ║
║   ██████╔╝   ██║   ██║     ╚█████╔╝╚█████╔╝███████║███████║ ║
║   ██╔══██╗   ██║   ██║     ██╔══██╗██╔══██╗╚════██║██╔══██║ ║
║   ██║  ██║   ██║   ███████╗╚█████╔╝╚█████╔╝     ██║██║  ██║ ║
║   ╚═╝  ╚═╝   ╚═╝   ╚══════╝ ╚════╝  ╚════╝      ╚═╝╚═╝  ╚═╝ ║
║                                                               ║
║            RTL8814AU USB WiFi Driver Installer                ║
║                   for macOS Sequoia (15.0+)                   ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝
EOF
echo -e "${NC}"

# Check if running on macOS
if [[ "$OSTYPE" != "darwin"* ]]; then
    echo -e "${RED}Error: This script only works on macOS${NC}"
    exit 1
fi

# Get macOS version
MACOS_VERSION=$(sw_vers -productVersion)
MACOS_MAJOR=$(echo "$MACOS_VERSION" | cut -d. -f1)

echo -e "${BLUE}System Information:${NC}"
echo "  macOS Version: $MACOS_VERSION"
echo "  Architecture: $(uname -m)"
echo "  SIP Status: $(csrutil status 2>/dev/null || echo 'Unknown')"
echo ""

# Function to show menu
show_menu() {
    echo -e "${YELLOW}═══════════════════════════════════════════════════════════${NC}"
    echo -e "${GREEN}What would you like to do?${NC}"
    echo -e "${YELLOW}═══════════════════════════════════════════════════════════${NC}"
    echo ""
    echo "  ${GREEN}1${NC}) ${CYAN}Install Driver${NC}          - Full automated installation"
    echo "  ${GREEN}2${NC}) ${CYAN}Uninstall Driver${NC}        - Remove installed driver"
    echo "  ${GREEN}3${NC}) ${CYAN}Check Requirements${NC}      - Verify system is ready"
    echo "  ${GREEN}4${NC}) ${CYAN}Verify Installation${NC}     - Check if driver is loaded"
    echo "  ${GREEN}5${NC}) ${CYAN}View Logs${NC}               - Show kernel/driver logs"
    echo "  ${GREEN}6${NC}) ${CYAN}USB Device Info${NC}         - List connected USB devices"
    echo "  ${GREEN}7${NC}) ${CYAN}Troubleshooting${NC}         - Common issues and fixes"
    echo "  ${GREEN}8${NC}) ${CYAN}About/Help${NC}              - More information"
    echo "  ${GREEN}9${NC}) ${RED}Exit${NC}"
    echo ""
    echo -e "${YELLOW}═══════════════════════════════════════════════════════════${NC}"
    echo ""
    echo -n "Enter your choice (1-9): "
}

# Function to check requirements
check_requirements() {
    echo -e "${YELLOW}Checking system requirements...${NC}"
    echo ""
    
    local all_ok=true
    
    # macOS version
    if [ $MACOS_MAJOR -ge 15 ]; then
        echo -e "  ${GREEN}✓${NC} macOS Sequoia or later: $MACOS_VERSION"
    else
        echo -e "  ${RED}✗${NC} macOS version too old: $MACOS_VERSION (need 15.0+)"
        all_ok=false
    fi
    
    # Homebrew
    if command -v brew &> /dev/null; then
        echo -e "  ${GREEN}✓${NC} Homebrew installed: $(brew --version | head -n1)"
    else
        echo -e "  ${YELLOW}⚠${NC} Homebrew not installed"
        all_ok=false
    fi
    
    # Xcode tools
    if xcode-select -p &> /dev/null; then
        echo -e "  ${GREEN}✓${NC} Xcode Command Line Tools installed"
    else
        echo -e "  ${RED}✗${NC} Xcode Command Line Tools not installed"
        all_ok=false
    fi
    
    # Git
    if command -v git &> /dev/null; then
        echo -e "  ${GREEN}✓${NC} Git installed"
    else
        echo -e "  ${YELLOW}⚠${NC} Git not installed (will install via Homebrew)"
    fi
    
    echo ""
    
    if $all_ok; then
        echo -e "${GREEN}✓ All requirements met!${NC}"
        return 0
    else
        echo -e "${YELLOW}⚠ Some requirements are missing${NC}"
        echo ""
        echo "Would you like to install missing components? (y/N)"
        read -r response
        if [[ "$response" =~ ^[Yy]$ ]]; then
            install_missing_requirements
        fi
        return 1
    fi
}

# Function to install missing requirements
install_missing_requirements() {
    echo -e "${YELLOW}Installing missing requirements...${NC}"
    echo ""
    
    # Install Homebrew if missing
    if ! command -v brew &> /dev/null; then
        echo "Installing Homebrew..."
        /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
        
        # Add to PATH
        if [[ -f "/opt/homebrew/bin/brew" ]]; then
            eval "$(/opt/homebrew/bin/brew shellenv)"
        elif [[ -f "/usr/local/bin/brew" ]]; then
            eval "$(/usr/local/bin/brew shellenv)"
        fi
    fi
    
    # Install Xcode tools if missing
    if ! xcode-select -p &> /dev/null; then
        echo "Installing Xcode Command Line Tools..."
        xcode-select --install
        echo ""
        echo -e "${YELLOW}Please complete the Xcode installation and run this script again${NC}"
        exit 0
    fi
    
    echo -e "${GREEN}✓ Requirements installed${NC}"
}

# Function to install driver
install_driver() {
    echo -e "${YELLOW}═══════════════════════════════════════════════════════════${NC}"
    echo -e "${CYAN}Driver Installation${NC}"
    echo -e "${YELLOW}═══════════════════════════════════════════════════════════${NC}"
    echo ""
    
    echo -e "${YELLOW}⚠  IMPORTANT WARNINGS:${NC}"
    echo "   • This installs a third-party kernel extension"
    echo "   • Not signed or endorsed by Apple"
    echo "   • May affect system stability"
    echo "   • You'll need to approve it in System Settings"
    echo "   • Requires a system restart"
    echo ""
    echo "Do you want to continue? (y/N)"
    read -r response
    
    if [[ ! "$response" =~ ^[Yy]$ ]]; then
        echo "Installation cancelled"
        return
    fi
    
    echo ""
    echo -e "${YELLOW}Starting installation...${NC}"
    echo ""
    
    # Run the main installation script
    if [ -f "install-rtl8814au.sh" ]; then
        bash install-rtl8814au.sh
    elif [ -f "Makefile" ]; then
        make install
    else
        echo -e "${RED}Error: Installation scripts not found${NC}"
        echo "Please ensure you have the installation files"
    fi
}

# Function to uninstall driver
uninstall_driver() {
    echo -e "${YELLOW}═══════════════════════════════════════════════════════════${NC}"
    echo -e "${CYAN}Driver Uninstallation${NC}"
    echo -e "${YELLOW}═══════════════════════════════════════════════════════════${NC}"
    echo ""
    
    echo "Are you sure you want to uninstall the driver? (y/N)"
    read -r response
    
    if [[ ! "$response" =~ ^[Yy]$ ]]; then
        echo "Uninstallation cancelled"
        return
    fi
    
    echo ""
    
    KEXT_PATH="/Library/Extensions/rtl8814au.kext"
    
    if [ -d "$KEXT_PATH" ]; then
        echo "Unloading driver..."
        sudo kextunload "$KEXT_PATH" 2>/dev/null || \
        sudo kmutil unload -p "$KEXT_PATH" 2>/dev/null || true
        
        echo "Removing driver..."
        sudo rm -rf "$KEXT_PATH"
        
        echo "Updating kernel cache..."
        sudo kmutil install --update-all 2>/dev/null || \
        sudo kextcache -i / 2>/dev/null || true
        
        echo ""
        echo -e "${GREEN}✓ Driver uninstalled successfully${NC}"
        echo ""
        echo "Please restart your Mac to complete the removal"
    else
        echo -e "${YELLOW}⚠ Driver not found at $KEXT_PATH${NC}"
    fi
}

# Function to verify installation
verify_installation() {
    echo -e "${YELLOW}═══════════════════════════════════════════════════════════${NC}"
    echo -e "${CYAN}Verifying Installation${NC}"
    echo -e "${YELLOW}═══════════════════════════════════════════════════════════${NC}"
    echo ""
    
    KEXT_PATH="/Library/Extensions/rtl8814au.kext"
    
    echo "1. Driver file:"
    if [ -d "$KEXT_PATH" ]; then
        echo -e "   ${GREEN}✓${NC} Present at $KEXT_PATH"
        ls -lh "$KEXT_PATH" | head -n1
    else
        echo -e "   ${RED}✗${NC} Not found at $KEXT_PATH"
    fi
    echo ""
    
    echo "2. Driver loaded:"
    if kextstat | grep -q rtl8814au; then
        echo -e "   ${GREEN}✓${NC} Driver is loaded"
        kextstat | grep rtl8814au
    else
        echo -e "   ${YELLOW}⚠${NC} Driver is not loaded"
        echo "   (Normal before restart or approval)"
    fi
    echo ""
    
    echo "3. USB device:"
    if system_profiler SPUSBDataType 2>/dev/null | grep -i realtek >/dev/null; then
        echo -e "   ${GREEN}✓${NC} Realtek device detected"
    else
        echo -e "   ${YELLOW}⚠${NC} No Realtek device found"
        echo "   Make sure your adapter is connected"
    fi
    echo ""
}

# Function to show logs
show_logs() {
    echo -e "${YELLOW}═══════════════════════════════════════════════════════════${NC}"
    echo -e "${CYAN}Recent Kernel Logs${NC}"
    echo -e "${YELLOW}═══════════════════════════════════════════════════════════${NC}"
    echo ""
    
    echo "Showing logs from last 10 minutes..."
    echo ""
    
    log show --predicate 'process == "kernel"' --last 10m 2>/dev/null | \
        grep -i -E 'rtl|8814au|usb|wifi' | tail -n 50 || \
        echo "No relevant logs found"
    
    echo ""
}

# Function to show USB info
show_usb_info() {
    echo -e "${YELLOW}═══════════════════════════════════════════════════════════${NC}"
    echo -e "${CYAN}USB Device Information${NC}"
    echo -e "${YELLOW}═══════════════════════════════════════════════════════════${NC}"
    echo ""
    
    echo "Scanning USB devices..."
    echo ""
    
    system_profiler SPUSBDataType 2>/dev/null | \
        grep -A 20 -i realtek || \
        echo "No Realtek USB devices found"
    
    echo ""
}

# Function to show troubleshooting
show_troubleshooting() {
    echo -e "${YELLOW}═══════════════════════════════════════════════════════════${NC}"
    echo -e "${CYAN}Troubleshooting Guide${NC}"
    echo -e "${YELLOW}═══════════════════════════════════════════════════════════${NC}"
    echo ""
    
    cat << EOF
${CYAN}Problem: Driver not loading after restart${NC}
Solution:
  1. Go to System Settings > Privacy & Security
  2. Look for blocked software notification
  3. Click "Allow" for rtl8814au
  4. Restart again

${CYAN}Problem: USB device not recognized${NC}
Solution:
  1. Try different USB port (preferably USB 3.0)
  2. Check: system_profiler SPUSBDataType
  3. Reconnect the adapter
  4. Try different USB cable

${CYAN}Problem: Build errors${NC}
Solution:
  1. Verify Xcode tools: xcode-select --install
  2. Update Homebrew: brew update
  3. Check logs for specific errors
  4. Clean and rebuild: make clean && make build

${CYAN}Problem: System Integrity Protection blocking${NC}
Solution:
  Option A (Recommended): Get Apple Developer ID and sign driver
  Option B: Temporarily disable SIP (see README.md)

${CYAN}Problem: Kernel panics or crashes${NC}
Solution:
  1. Boot into Safe Mode (hold Shift during boot)
  2. Run: sudo rm -rf /Library/Extensions/rtl8814au.kext
  3. Restart normally
  4. Check compatibility or try different driver version

${CYAN}For more help:${NC}
  • Check README.md for detailed documentation
  • View logs: make logs
  • Search GitHub issues
  • macOS Console app (Kernel category)

EOF
}

# Function to show about/help
show_about() {
    echo -e "${YELLOW}═══════════════════════════════════════════════════════════${NC}"
    echo -e "${CYAN}About RTL8814AU Driver${NC}"
    echo -e "${YELLOW}═══════════════════════════════════════════════════════════${NC}"
    echo ""
    
    cat << EOF
${CYAN}What is RTL8814AU?${NC}
The RTL8814AU is a USB WiFi chipset made by Realtek, found in many
AC1900 dual-band WiFi adapters. This driver enables these adapters
to work on macOS Sequoia.

${CYAN}Supported Devices:${NC}
  • ALFA AWUS1900
  • Edimax EW-7833UAC
  • ASUS USB-AC68
  • TP-Link Archer T9UH
  • Many generic "AC1900" adapters

${CYAN}Features:${NC}
  • 802.11ac WiFi (up to 1900 Mbps)
  • Dual-band (2.4 GHz and 5 GHz)
  • Monitor mode support
  • Open-source driver

${CYAN}System Requirements:${NC}
  • macOS Sequoia 15.0 or later
  • Intel or Apple Silicon Mac
  • 2GB free disk space
  • Administrator access

${CYAN}Important Notes:${NC}
  ⚠️  This is an unofficial, community-maintained driver
  ⚠️  Not signed or endorsed by Apple or Realtek
  ⚠️  Requires kernel extension approval
  ⚠️  Use at your own risk

${CYAN}Documentation:${NC}
  • README.md - Full documentation
  • GitHub repository for updates
  • Community support forums

${CYAN}Project:${NC}
  Based on: https://github.com/morrownr/8814au
  License: GPL-2.0

EOF
}

# Main loop
while true; do
    show_menu
    read -r choice
    echo ""
    
    case $choice in
        1)
            install_driver
            ;;
        2)
            uninstall_driver
            ;;
        3)
            check_requirements
            ;;
        4)
            verify_installation
            ;;
        5)
            show_logs
            ;;
        6)
            show_usb_info
            ;;
        7)
            show_troubleshooting
            ;;
        8)
            show_about
            ;;
        9)
            echo -e "${GREEN}Thank you for using RTL8814AU Driver Installer!${NC}"
            exit 0
            ;;
        *)
            echo -e "${RED}Invalid choice. Please enter 1-9.${NC}"
            ;;
    esac
    
    echo ""
    echo -e "${YELLOW}Press Enter to continue...${NC}"
    read -r
    clear
done
