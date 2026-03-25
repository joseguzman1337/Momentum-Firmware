#!/bin/bash
set -e

echo "🗑️  Uninstalling RTL8814AU Driver..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if running as root
if [[ $EUID -ne 0 ]]; then
   echo -e "${RED}Error: This script must be run as root (use sudo)${NC}"
   exit 1
fi

INSTALL_APP_PATH="/Applications/RTL8814AUDriver.app"
BUNDLE_ID="com.rtl8814au.driver"

# Check if installed
if [[ ! -d "$INSTALL_APP_PATH" ]]; then
    echo -e "${YELLOW}Driver is not installed at $INSTALL_APP_PATH${NC}"
    exit 0
fi

# Unload system extension
echo "🛑 Unloading system extension..."
if systemextensionsctl list | grep -q "$BUNDLE_ID"; then
    "$INSTALL_APP_PATH/Contents/MacOS/RTL8814AUApp" uninstall
    
    if [[ $? -eq 0 ]]; then
        echo "✅ System extension unloaded"
    else
        echo -e "${YELLOW}⚠️  Failed to unload system extension${NC}"
        echo "You may need to reboot to complete uninstallation"
    fi
else
    echo "No active system extension found"
fi

# Remove application
echo "🗑️  Removing application..."
rm -rf "$INSTALL_APP_PATH"
echo "✅ Application removed"

# Check for any remaining system extensions
REMAINING=$(systemextensionsctl list | grep "$BUNDLE_ID" || true)
if [[ -n "$REMAINING" ]]; then
    echo -e "${YELLOW}⚠️  System extension still present (may require reboot to fully remove):${NC}"
    echo "$REMAINING"
    echo ""
    echo "Please reboot your Mac to complete the uninstallation."
else
    echo -e "${GREEN}✅ Driver completely uninstalled${NC}"
fi

echo ""
echo "Uninstallation complete."
