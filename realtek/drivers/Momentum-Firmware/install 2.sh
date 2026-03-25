#!/bin/bash

# RTL8814AU Driver Installation Script

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}================================${NC}"
echo -e "${GREEN}RTL8814AU Driver Installer${NC}"
echo -e "${GREEN}================================${NC}"
echo ""

# Check for root
if [ "$EUID" -ne 0 ]; then
    echo -e "${RED}Please run as root using sudo:${NC}"
    echo "sudo ./install.sh"
    exit 1
fi

# Configuration
DEXT_PATH="build/RTL8814AUDriver.dext"
INSTALL_DIR="/Library/SystemExtensions"
BUNDLE_ID="com.opensource.RTL8814AUDriver"

# Check if driver exists
if [ ! -d "$DEXT_PATH" ]; then
    echo -e "${RED}Error: Driver not found at $DEXT_PATH${NC}"
    echo "Please run ./build.sh first"
    exit 1
fi

# Check SIP status
echo -e "${YELLOW}Checking System Integrity Protection status...${NC}"
SIP_STATUS=$(csrutil status)
echo "$SIP_STATUS"

if echo "$SIP_STATUS" | grep -q "disabled"; then
    echo -e "${RED}Warning: SIP is disabled. This driver is designed to work with SIP enabled.${NC}"
    echo -e "${YELLOW}Consider enabling SIP for better security.${NC}"
fi

# Verify signature
echo ""
echo -e "${YELLOW}Verifying driver signature...${NC}"
codesign -vvv --deep --strict "$DEXT_PATH"

if [ $? -ne 0 ]; then
    echo -e "${RED}Error: Driver signature is invalid!${NC}"
    echo "Please run ./sign.sh to sign the driver properly."
    exit 1
fi

echo -e "${GREEN}Driver signature verified.${NC}"

# Check for existing installation
echo ""
echo -e "${YELLOW}Checking for existing installation...${NC}"

EXISTING_DEXT=$(find "$INSTALL_DIR" -name "RTL8814AUDriver.dext" 2>/dev/null || true)

if [ -n "$EXISTING_DEXT" ]; then
    echo -e "${YELLOW}Found existing driver installation.${NC}"
    echo -e "${YELLOW}Uninstalling old version...${NC}"
    
    # Deactivate system extension
    systemextensionsctl uninstall "$BUNDLE_ID" "$BUNDLE_ID" 2>/dev/null || true
    
    # Wait for uninstall
    sleep 2
    
    # Remove old files
    rm -rf "$EXISTING_DEXT" 2>/dev/null || true
fi

# Create installation directory if needed
mkdir -p "$INSTALL_DIR"

# Copy driver
echo ""
echo -e "${YELLOW}Installing driver...${NC}"
cp -R "$DEXT_PATH" "$INSTALL_DIR/"

# Set permissions
chmod -R 755 "$INSTALL_DIR/RTL8814AUDriver.dext"

# Verify installation
INSTALLED_PATH="$INSTALL_DIR/RTL8814AUDriver.dext"

if [ ! -d "$INSTALLED_PATH" ]; then
    echo -e "${RED}Error: Installation failed${NC}"
    exit 1
fi

echo -e "${GREEN}Driver installed to: $INSTALLED_PATH${NC}"

# Load the extension
echo ""
echo -e "${YELLOW}Activating system extension...${NC}"
systemextensionsctl developer on 2>/dev/null || true

echo ""
echo -e "${GREEN}================================${NC}"
echo -e "${GREEN}Installation Complete!${NC}"
echo -e "${GREEN}================================${NC}"
echo ""

echo -e "${YELLOW}IMPORTANT NEXT STEPS:${NC}"
echo ""
echo "1. You will receive a system notification asking to allow the system extension"
echo "   ${YELLOW}Click 'Allow' in the notification${NC}"
echo ""
echo "2. Open System Settings → Privacy & Security"
echo "   ${YELLOW}Scroll down and click 'Allow' next to the driver extension${NC}"
echo ""
echo "3. Restart your Mac for the changes to take effect"
echo ""
echo "4. After restart, connect your RTL8814AU USB WiFi adapter"
echo ""
echo "5. Check installation with:"
echo "   ${GREEN}systemextensionsctl list${NC}"
echo ""
echo "6. Monitor driver logs with:"
echo "   ${GREEN}log stream --predicate 'subsystem == \"$BUNDLE_ID\"'${NC}"
echo ""

# Show current system extensions
echo -e "${YELLOW}Current system extensions:${NC}"
systemextensionsctl list

echo ""
echo -e "${YELLOW}Troubleshooting:${NC}"
echo "- If the driver doesn't load, check System Settings → Privacy & Security"
echo "- View logs: log show --predicate 'subsystem == \"$BUNDLE_ID\"' --last 1h"
echo "- Uninstall: sudo systemextensionsctl uninstall $BUNDLE_ID $BUNDLE_ID"
echo ""
