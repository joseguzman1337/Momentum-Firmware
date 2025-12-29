#!/bin/bash
set -e

echo "📦 Installing RTL8814AU Driver for macOS Sequoia..."

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

# Check if build exists
BUILD_DIR="build/Output"
if [[ ! -d "$BUILD_DIR" ]]; then
    echo -e "${RED}Error: Build not found. Please run './build.sh' first.${NC}"
    exit 1
fi

# Find driver extension
DRIVER_PATH=$(find "$BUILD_DIR" -name "*.dext" -type d | head -n 1)
APP_PATH=$(find "$BUILD_DIR" -name "RTL8814AUApp.app" -type d | head -n 1)

if [[ -z "$DRIVER_PATH" ]]; then
    echo -e "${RED}Error: Driver extension (.dext) not found in build output${NC}"
    exit 1
fi

if [[ -z "$APP_PATH" ]]; then
    echo -e "${RED}Error: Helper application not found in build output${NC}"
    exit 1
fi

echo "📋 Found driver at: $DRIVER_PATH"
echo "📋 Found helper app at: $APP_PATH"

# Installation paths
INSTALL_APP_PATH="/Applications/RTL8814AUDriver.app"
DRIVER_NAME=$(basename "$DRIVER_PATH")

# Stop and unload existing driver if installed
echo "🛑 Stopping existing driver (if any)..."
BUNDLE_ID="com.rtl8814au.driver"
systemextensionsctl list | grep "$BUNDLE_ID" &> /dev/null && {
    echo "Found existing installation, unloading..."
    # The helper app will handle unloading
    if [[ -f "$INSTALL_APP_PATH/Contents/MacOS/RTL8814AUApp" ]]; then
        sudo "$INSTALL_APP_PATH/Contents/MacOS/RTL8814AUApp" uninstall || true
    fi
}

# Install helper application
echo "📦 Installing helper application..."
if [[ -d "$INSTALL_APP_PATH" ]]; then
    rm -rf "$INSTALL_APP_PATH"
fi
cp -R "$APP_PATH" "$INSTALL_APP_PATH"
chown -R root:wheel "$INSTALL_APP_PATH"
chmod -R 755 "$INSTALL_APP_PATH"

echo "✅ Helper application installed"

# Install and activate system extension
echo "🔧 Installing system extension..."
"$INSTALL_APP_PATH/Contents/MacOS/RTL8814AUApp" install

if [[ $? -eq 0 ]]; then
    echo -e "${GREEN}✅ Driver installed successfully!${NC}"
    echo ""
    echo -e "${YELLOW}⚠️  IMPORTANT: Complete the installation by following these steps:${NC}"
    echo ""
    echo "1. Open System Settings"
    echo "2. Go to Privacy & Security"
    echo "3. Scroll down and approve the system extension from your developer team"
    echo "4. You may be prompted to restart your Mac"
    echo ""
    echo "After approval, plug in your RTL8814AU device and it should be recognized."
    echo ""
    echo "To check if the driver is loaded, run:"
    echo "  systemextensionsctl list"
    echo ""
    echo "To view driver logs, run:"
    echo "  log show --predicate 'subsystem == \"com.rtl8814au.driver\"' --last 1h"
else
    echo -e "${RED}❌ Installation failed${NC}"
    echo "Check System Settings > Privacy & Security for more information"
    exit 1
fi

# Check SIP status
echo ""
echo "🔒 Checking System Integrity Protection status..."
SIP_STATUS=$(csrutil status)
if echo "$SIP_STATUS" | grep -q "enabled"; then
    echo -e "${GREEN}✅ SIP is enabled (recommended)${NC}"
elif echo "$SIP_STATUS" | grep -q "disabled"; then
    echo -e "${YELLOW}⚠️  SIP is disabled. This driver works with SIP enabled.${NC}"
else
    echo -e "${YELLOW}⚠️  Could not determine SIP status${NC}"
fi

echo ""
echo -e "${GREEN}Installation process complete!${NC}"
