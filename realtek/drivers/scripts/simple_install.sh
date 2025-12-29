#!/bin/bash

# RTL88xxAU macOS Driver - Simplified Installer
# This version works around modern macOS security restrictions

set -e

DRIVER_NAME="RTL88xxAU"
KEXT_NAME="${DRIVER_NAME}.kext"
BUILD_DIR="build"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running as root
if [ "$(id -u)" != "0" ]; then
    print_error "This script must be run as root (use sudo)"
    exit 1
fi

echo "======================================="
echo "RTL88xxAU Simplified Driver Installer"
echo "======================================="
echo

# Get macOS version info
MACOS_VERSION=$(sw_vers -productVersion)
MACOS_MAJOR=$(echo $MACOS_VERSION | cut -d. -f1)

print_status "Detected macOS version: $MACOS_VERSION"

# Determine installation directory based on macOS version
if [ "$MACOS_MAJOR" -ge 11 ]; then
    # Modern macOS - try /Library/Extensions first
    if [ -d "/Library/Extensions" ]; then
        INSTALL_DIR="/Library/Extensions"
        print_status "Using /Library/Extensions for modern macOS"
    else
        INSTALL_DIR="/System/Library/Extensions"
        print_warning "Using legacy path - may require SIP to be disabled"
    fi
else
    INSTALL_DIR="/System/Library/Extensions"
fi

print_status "Installation directory: $INSTALL_DIR"

# Check if build exists
if [ ! -d "$BUILD_DIR/$KEXT_NAME" ]; then
    print_status "Building driver..."
    if [ -f "Makefile" ]; then
        make clean
        make build
    else
        print_error "No build found and no Makefile available"
        exit 1
    fi
fi

# Unload existing driver if loaded
if kextstat | grep -q "$DRIVER_NAME"; then
    print_status "Unloading existing driver..."
    kextunload "$INSTALL_DIR/$KEXT_NAME" 2>/dev/null || true
fi

# Remove old installation
if [ -d "$INSTALL_DIR/$KEXT_NAME" ]; then
    print_status "Removing old installation..."
    rm -rf "$INSTALL_DIR/$KEXT_NAME"
fi

# Install new driver
print_status "Installing driver..."
cp -R "$BUILD_DIR/$KEXT_NAME" "$INSTALL_DIR/"

# Set permissions
chown -R root:wheel "$INSTALL_DIR/$KEXT_NAME"
chmod -R 755 "$INSTALL_DIR/$KEXT_NAME"
chmod 644 "$INSTALL_DIR/$KEXT_NAME/Contents/Info.plist"

print_success "Driver files installed"

# Update kernel cache
print_status "Updating kernel extension cache..."
kextcache -system-caches 2>/dev/null || {
    print_warning "Failed to update kernel cache - this may be due to SIP"
    print_status "Driver files are installed but may require a restart"
}

# Try to load the driver
print_status "Attempting to load driver..."
if kextload "$INSTALL_DIR/$KEXT_NAME" 2>/dev/null; then
    print_success "Driver loaded successfully!"
    
    # Verify it's running
    sleep 2
    if kextstat | grep -q "$DRIVER_NAME"; then
        print_success "Driver is active and running"
        print_status "Installation completed successfully!"
        print_status "Your RTL88xxAU device should now be available"
    else
        print_warning "Driver files installed but not currently loaded"
        print_status "Please restart your Mac to complete installation"
    fi
else
    print_warning "Could not load driver immediately"
    print_status "This is normal on systems with SIP enabled"
    print_status "Driver files are installed - please restart your Mac"
fi

echo
print_status "Installation completed!"
print_status "If the driver doesn't work after restart, you may need to:"
print_status "1. Disable SIP temporarily"
print_status "2. Check System Preferences > Security & Privacy for any prompts"
print_status "3. Reconnect your RTL88xxAU USB device"
