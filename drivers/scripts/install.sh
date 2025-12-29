#!/bin/bash

# RTL88xxAU macOS Driver Installation Script
# Copyright (c) 2024 Realtek

set -e

DRIVER_NAME="RTL88xxAU"
KEXT_NAME="${DRIVER_NAME}.kext"
# Default installation directory (may be changed based on SIP status)
INSTALL_DIR="/System/Library/Extensions"
BUILD_DIR="build"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Print colored output
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
check_root() {
    if [ "$(id -u)" != "0" ]; then
        print_error "This script must be run as root (use sudo)"
        exit 1
    fi
}

# Check macOS version
check_macos_version() {
    local macos_version=$(sw_vers -productVersion)
    local major_version=$(echo $macos_version | cut -d. -f1)
    local minor_version=$(echo $macos_version | cut -d. -f2 | sed 's/[^0-9].*//g')
    
    print_status "Detected macOS version: $macos_version"
    
    # Handle macOS versioning (Big Sur 11.x, Monterey 12.x, Ventura 13.x, Sonoma 14.x, Sequoia 15.x, etc.)
    if [ "$major_version" -ge 15 ] || [ "$major_version" -ge 14 ] || [ "$major_version" -ge 13 ] || [ "$major_version" -ge 12 ]; then
        print_success "macOS version is supported (modern macOS)"
    elif [ "$major_version" -eq 11 ] && [ "${minor_version:-0}" -ge 0 ]; then
        print_success "macOS version is supported (Big Sur)"
    elif [ "$major_version" -lt 11 ]; then
        print_error "This driver requires macOS 11.0 (Big Sur) or later"
        exit 1
    else
        print_success "macOS version is supported"
    fi
}

# Check for Xcode command line tools
check_xcode() {
    if ! xcode-select -p &> /dev/null; then
        print_warning "Xcode command line tools not found"
        print_status "Installing Xcode command line tools..."
        xcode-select --install
        print_status "Please run this script again after installing Xcode command line tools"
        exit 0
    fi
    
    print_success "Xcode command line tools found"
}

# Check System Integrity Protection
check_sip() {
    local sip_status=$(csrutil status 2>/dev/null || echo "unknown")
    
    if echo "$sip_status" | grep -q "enabled"; then
        print_warning "System Integrity Protection (SIP) is enabled"
        print_status "Modern macOS may require SIP to be temporarily disabled for kernel extensions"
        print_status "Alternative: We'll try to install using modern methods first"
        echo
        
        # Try to continue with modern installation methods
        print_status "Attempting installation with SIP enabled..."
        
        # For modern macOS, we can try installing to /Library/Extensions instead
        if [ -d "/Library/Extensions" ]; then
            INSTALL_DIR="/Library/Extensions"
            print_status "Using /Library/Extensions for modern macOS compatibility"
        fi
        
    else
        print_success "System Integrity Protection is disabled or not found"
    fi
}

# Detect connected RTL devices
detect_devices() {
    print_status "Scanning for RTL88xxAU devices..."
    
    local devices=$(system_profiler SPUSBDataType 2>/dev/null | grep -i realtek || true)
    
    if [ -n "$devices" ]; then
        print_success "Found Realtek USB device(s):"
        echo "$devices"
    else
        print_warning "No Realtek USB devices detected"
        print_status "Please ensure your RTL88xxAU device is connected"
    fi
}

# Unload existing driver
unload_existing() {
    print_status "Checking for existing RTL drivers..."
    
    # Check if our driver is loaded
    if kextstat | grep -q "$DRIVER_NAME"; then
        print_status "Unloading existing $DRIVER_NAME driver..."
        kextunload "$INSTALL_DIR/$KEXT_NAME" || true
    fi
    
    # Check for other RTL drivers
    local other_drivers=$(kextstat | grep -i realtek | grep -v "$DRIVER_NAME" || true)
    if [ -n "$other_drivers" ]; then
        print_warning "Found other Realtek drivers loaded:"
        echo "$other_drivers"
        print_warning "These may conflict with the new driver"
    fi
}

# Remove old installation
remove_old() {
    if [ -d "$INSTALL_DIR/$KEXT_NAME" ]; then
        print_status "Removing old driver installation..."
        rm -rf "$INSTALL_DIR/$KEXT_NAME"
    fi
}

# Build the driver
build_driver() {
    print_status "Building RTL88xxAU driver..."
    
    if [ ! -f "Makefile" ]; then
        print_error "Makefile not found. Please run this script from the driver source directory"
        exit 1
    fi
    
    make clean
    make build
    
    if [ ! -d "$BUILD_DIR/$KEXT_NAME" ]; then
        print_error "Build failed - kernel extension not found"
        exit 1
    fi
    
    print_success "Driver built successfully"
}

# Install the driver
install_driver() {
    print_status "Installing RTL88xxAU driver to $INSTALL_DIR..."
    
    # Copy the kext
    cp -R "$BUILD_DIR/$KEXT_NAME" "$INSTALL_DIR/"
    
    # Set correct permissions
    chown -R root:wheel "$INSTALL_DIR/$KEXT_NAME"
    chmod -R 755 "$INSTALL_DIR/$KEXT_NAME"
    chmod 644 "$INSTALL_DIR/$KEXT_NAME/Contents/Info.plist"
    
    print_success "Driver installed"
}

# Update kernel extension cache
update_cache() {
    print_status "Updating kernel extension cache..."
    kextcache -system-caches
    print_success "Kernel extension cache updated"
}

# Load the driver
load_driver() {
    print_status "Loading RTL88xxAU driver..."
    
    if kextload "$INSTALL_DIR/$KEXT_NAME"; then
        print_success "Driver loaded successfully"
    else
        print_error "Failed to load driver"
        print_status "Check system logs for details: log show --predicate 'senderImagePath contains \"RTL88xxAU\"'"
        return 1
    fi
}

# Verify installation
verify_installation() {
    print_status "Verifying installation..."
    
    if kextstat | grep -q "$DRIVER_NAME"; then
        print_success "Driver is loaded and running"
        
        # Check for network interfaces
        sleep 2
        local interfaces=$(networksetup -listallhardwareports | grep -A1 -i wifi || true)
        if [ -n "$interfaces" ]; then
            print_success "Network interfaces found:"
            echo "$interfaces"
        fi
        
        return 0
    else
        print_error "Driver is not loaded"
        return 1
    fi
}

# Main installation function
main() {
    echo "======================================"
    echo "RTL88xxAU macOS Driver Installer"
    echo "======================================"
    echo
    
    check_root
    check_macos_version
    check_xcode
    check_sip
    detect_devices
    
    echo
    print_status "Starting installation..."
    
    unload_existing
    remove_old
    build_driver
    install_driver
    update_cache
    
    if load_driver && verify_installation; then
        echo
        print_success "Installation completed successfully!"
        print_status "Your RTL88xxAU device should now be available in Network Preferences"
        print_status "You may need to restart your Mac or reconnect the USB device"
    else
        echo
        print_error "Installation completed but driver failed to load"
        print_status "Try the following:"
        print_status "1. Restart your Mac"
        print_status "2. Check System Integrity Protection: csrutil status"
        print_status "3. Check system logs: log show --predicate 'senderImagePath contains \"RTL88xxAU\"'"
        print_status "4. Manually load: sudo kextload $INSTALL_DIR/$KEXT_NAME"
    fi
}

# Cleanup function
cleanup() {
    print_status "Cleaning up temporary files..."
    # Add any cleanup tasks here
}

# Set up error handling
trap cleanup EXIT

# Run main installation
main "$@"
