#!/bin/bash

# RTL8814AU Driver Auto-Installer for macOS Sequoia
# This script automates the entire process of building and installing
# the RTL8814AU driver with proper checks and balances

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
DRIVER_REPO="https://github.com/morrownr/8814au.git"
BUILD_DIR="$HOME/rtl8814au-build"
DRIVER_NAME="rtl8814au"
KEXT_NAME="${DRIVER_NAME}.kext"
INSTALL_PATH="/Library/Extensions/${KEXT_NAME}"

# Functions
print_header() {
    echo -e "${BLUE}"
    echo "================================================================"
    echo "  RTL8814AU Driver Auto-Installer for macOS Sequoia"
    echo "================================================================"
    echo -e "${NC}"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ $1${NC}"
}

# Check if running on macOS
check_macos() {
    print_info "Checking operating system..."
    if [[ "$OSTYPE" != "darwin"* ]]; then
        print_error "This script only works on macOS"
        exit 1
    fi
    
    # Get macOS version
    MACOS_VERSION=$(sw_vers -productVersion)
    MACOS_MAJOR=$(echo "$MACOS_VERSION" | cut -d. -f1)
    MACOS_MINOR=$(echo "$MACOS_VERSION" | cut -d. -f2)
    
    print_success "Running macOS $MACOS_VERSION"
    
    if [[ $MACOS_MAJOR -lt 15 ]]; then
        print_warning "This script is optimized for macOS Sequoia (15.0+)"
        print_warning "Your version: $MACOS_VERSION"
        read -p "Continue anyway? (y/N) " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    fi
}

# Check System Integrity Protection
check_sip() {
    print_info "Checking System Integrity Protection (SIP)..."
    SIP_STATUS=$(csrutil status 2>/dev/null || echo "unknown")
    
    echo "  $SIP_STATUS"
    
    if [[ "$SIP_STATUS" == *"enabled"* ]]; then
        print_warning "SIP is ENABLED"
        echo ""
        echo "  With SIP enabled on macOS Sequoia, kernel extension installation"
        echo "  is restricted. You have several options:"
        echo ""
        echo "  Option 1 (RECOMMENDED): Keep SIP enabled"
        echo "    - Requires Apple Developer Program membership (\$99/year)"
        echo "    - Driver must be code-signed with Developer ID"
        echo "    - Driver must be notarized by Apple"
        echo "    - User approves in System Settings > Privacy & Security"
        echo ""
        echo "  Option 2: Temporarily disable SIP (NOT RECOMMENDED)"
        echo "    - Boot into Recovery Mode (Cmd+R during startup)"
        echo "    - Open Terminal from Utilities menu"
        echo "    - Run: csrutil disable"
        echo "    - Restart and install driver"
        echo "    - Re-enable SIP: csrutil enable"
        echo ""
        echo "  Option 3: Use a USB WiFi adapter with native macOS support"
        echo ""
        
        print_info "This script will continue but installation may require approval"
        sleep 2
    else
        print_success "SIP is disabled or in permissive mode"
    fi
}

# Check for Homebrew
check_homebrew() {
    print_info "Checking for Homebrew..."
    
    if command -v brew &> /dev/null; then
        BREW_PATH=$(which brew)
        print_success "Homebrew found at: $BREW_PATH"
        BREW_VERSION=$(brew --version | head -n1)
        echo "  $BREW_VERSION"
    else
        print_error "Homebrew not found"
        echo ""
        echo "  Installing Homebrew..."
        /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
        
        # Add Homebrew to PATH
        if [[ -f "/opt/homebrew/bin/brew" ]]; then
            eval "$(/opt/homebrew/bin/brew shellenv)"
        elif [[ -f "/usr/local/bin/brew" ]]; then
            eval "$(/usr/local/bin/brew shellenv)"
        fi
        
        print_success "Homebrew installed"
    fi
}

# Check for Xcode Command Line Tools
check_xcode_tools() {
    print_info "Checking for Xcode Command Line Tools..."
    
    if xcode-select -p &> /dev/null; then
        XCODE_PATH=$(xcode-select -p)
        print_success "Xcode Command Line Tools found at: $XCODE_PATH"
    else
        print_error "Xcode Command Line Tools not found"
        echo "  Installing Command Line Tools..."
        xcode-select --install
        
        echo ""
        print_warning "Please complete the Xcode Command Line Tools installation"
        print_warning "and run this script again"
        exit 1
    fi
}

# Install dependencies
install_dependencies() {
    print_info "Installing dependencies via Homebrew..."
    
    DEPENDENCIES=("git" "cmake" "pkg-config" "openssl@3")
    
    for dep in "${DEPENDENCIES[@]}"; do
        if brew list "$dep" &> /dev/null; then
            print_success "$dep already installed"
        else
            echo "  Installing $dep..."
            brew install "$dep"
            print_success "$dep installed"
        fi
    done
}

# Clone driver source
clone_driver_source() {
    print_info "Cloning driver source code..."
    
    # Clean up old build directory
    if [[ -d "$BUILD_DIR" ]]; then
        print_warning "Removing old build directory..."
        rm -rf "$BUILD_DIR"
    fi
    
    # Clone repository
    git clone "$DRIVER_REPO" "$BUILD_DIR"
    cd "$BUILD_DIR"
    
    print_success "Source code cloned to: $BUILD_DIR"
    
    # Show latest commit
    LATEST_COMMIT=$(git log -1 --pretty=format:"%h - %s (%cr)")
    echo "  Latest: $LATEST_COMMIT"
}

# Configure build for macOS Sequoia
configure_build() {
    print_info "Configuring build for macOS Sequoia..."
    
    cd "$BUILD_DIR"
    
    # Detect architecture
    ARCH=$(uname -m)
    print_info "Architecture: $ARCH"
    
    # Create configuration file
    cat > platform.config << EOF
# macOS Sequoia Configuration
CONFIG_PLATFORM_MACOS=y
CONFIG_PLATFORM_ARM_MAC=$([ "$ARCH" = "arm64" ] && echo "y" || echo "n")
CONFIG_PLATFORM_I386_PC=$([ "$ARCH" = "x86_64" ] && echo "y" || echo "n")
CONFIG_80211AC_SUPPORT=y
CONFIG_WIFI_MONITOR=y
EOF

    print_success "Build configured for $ARCH architecture"
}

# Build driver
build_driver() {
    print_info "Building driver..."
    
    cd "$BUILD_DIR"
    
    # Clean previous builds
    make clean &> /dev/null || true
    
    # Build with all CPU cores
    NUM_CORES=$(sysctl -n hw.ncpu)
    print_info "Building with $NUM_CORES cores..."
    
    if make -j"$NUM_CORES" 2>&1 | tee build.log; then
        print_success "Driver built successfully"
    else
        print_error "Build failed. Check $BUILD_DIR/build.log for details"
        exit 1
    fi
}

# Check for code signing certificate
check_code_signing() {
    print_info "Checking for code signing certificate..."
    
    SIGNING_IDENTITY=$(security find-identity -v -p codesigning 2>/dev/null | grep "Developer ID" | head -n1 | sed 's/.*"\(.*\)".*/\1/')
    
    if [[ -n "$SIGNING_IDENTITY" ]]; then
        print_success "Found signing identity: $SIGNING_IDENTITY"
        return 0
    else
        print_warning "No Developer ID certificate found"
        echo "  The driver will be unsigned."
        echo "  For production use, you need:"
        echo "    1. Apple Developer Program membership"
        echo "    2. Developer ID Application certificate"
        echo "    3. Notarization by Apple"
        return 1
    fi
}

# Sign driver (if certificate available)
sign_driver() {
    cd "$BUILD_DIR"
    
    if check_code_signing; then
        print_info "Signing driver..."
        
        if [[ -d "$KEXT_NAME" ]]; then
            codesign --force --deep --sign "$SIGNING_IDENTITY" "$KEXT_NAME" 2>&1 | tee sign.log
            
            # Verify signature
            if codesign --verify --verbose "$KEXT_NAME" 2>&1 | tee -a sign.log; then
                print_success "Driver signed successfully"
            else
                print_warning "Signature verification failed"
            fi
        else
            print_error "Kernel extension not found: $KEXT_NAME"
            exit 1
        fi
    else
        print_warning "Skipping code signing (no certificate)"
    fi
}

# Install driver
install_driver() {
    print_info "Installing driver..."
    
    cd "$BUILD_DIR"
    
    if [[ $EUID -ne 0 ]]; then
        print_warning "Installation requires administrator privileges"
        echo "  You will be prompted for your password"
        echo ""
    fi
    
    # Backup existing driver if present
    if [[ -d "$INSTALL_PATH" ]]; then
        BACKUP_PATH="${INSTALL_PATH}.backup.$(date +%Y%m%d_%H%M%S)"
        print_info "Backing up existing driver to: $BACKUP_PATH"
        sudo mv "$INSTALL_PATH" "$BACKUP_PATH"
    fi
    
    # Copy new driver
    if [[ -d "$KEXT_NAME" ]]; then
        print_info "Copying driver to: $INSTALL_PATH"
        sudo cp -R "$KEXT_NAME" "$INSTALL_PATH"
        
        # Set proper ownership and permissions
        sudo chown -R root:wheel "$INSTALL_PATH"
        sudo chmod -R 755 "$INSTALL_PATH"
        
        print_success "Driver installed to: $INSTALL_PATH"
    else
        print_error "Driver file not found: $BUILD_DIR/$KEXT_NAME"
        exit 1
    fi
    
    # Update kernel extension cache
    print_info "Updating kernel extension cache..."
    sudo kmutil install --update-all 2>/dev/null || sudo kextcache -i / 2>/dev/null || true
    
    print_success "Kernel extension cache updated"
}

# Post-installation instructions
post_install_instructions() {
    echo ""
    echo -e "${GREEN}"
    echo "================================================================"
    echo "  Installation Complete!"
    echo "================================================================"
    echo -e "${NC}"
    echo ""
    print_info "Next Steps:"
    echo ""
    echo "  1. RESTART YOUR MAC"
    echo "     The driver requires a reboot to take effect."
    echo ""
    echo "  2. APPROVE THE KERNEL EXTENSION (if prompted)"
    echo "     - Go to: System Settings > Privacy & Security"
    echo "     - Look for a notification about blocked system extension"
    echo "     - Click 'Allow' for the rtl8814au driver"
    echo "     - You may need to restart again after approval"
    echo ""
    echo "  3. VERIFY INSTALLATION"
    echo "     After restart, run:"
    echo "       kextstat | grep rtl8814au"
    echo ""
    echo "     Check if your adapter is recognized:"
    echo "       system_profiler SPUSBDataType | grep -A 10 Realtek"
    echo ""
    echo "  4. CONFIGURE NETWORK"
    echo "     - Go to: System Settings > Network"
    echo "     - Your RTL8814AU adapter should appear"
    echo "     - Configure WiFi settings as needed"
    echo ""
    print_info "Troubleshooting:"
    echo ""
    echo "  • View kernel messages:"
    echo "      log show --predicate 'process == \"kernel\"' --last 5m | grep -i rtl"
    echo ""
    echo "  • Check loaded extensions:"
    echo "      kextstat | grep -v com.apple"
    echo ""
    echo "  • Uninstall driver:"
    echo "      sudo kextunload '$INSTALL_PATH'"
    echo "      sudo rm -rf '$INSTALL_PATH'"
    echo ""
    print_warning "Security Note:"
    echo "  This is an open-source, community-maintained driver."
    echo "  It is not signed or endorsed by Apple or Realtek."
    echo "  Use at your own risk."
    echo ""
}

# Create uninstall script
create_uninstall_script() {
    UNINSTALL_SCRIPT="$HOME/uninstall-rtl8814au.sh"
    
    cat > "$UNINSTALL_SCRIPT" << 'EOF'
#!/bin/bash

# RTL8814AU Driver Uninstaller

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

KEXT_PATH="/Library/Extensions/rtl8814au.kext"

echo -e "${YELLOW}"
echo "RTL8814AU Driver Uninstaller"
echo "=============================="
echo -e "${NC}"
echo ""

if [[ $EUID -ne 0 ]]; then
   echo -e "${RED}This script must be run as root (use sudo)${NC}"
   exit 1
fi

if [[ -d "$KEXT_PATH" ]]; then
    echo "Unloading driver..."
    kextunload "$KEXT_PATH" 2>/dev/null || kmutil unload -p "$KEXT_PATH" 2>/dev/null || true
    
    echo "Removing driver..."
    rm -rf "$KEXT_PATH"
    
    echo "Updating kernel extension cache..."
    kmutil install --update-all 2>/dev/null || kextcache -i / 2>/dev/null || true
    
    echo -e "${GREEN}"
    echo "✓ Driver uninstalled successfully!"
    echo -e "${NC}"
    echo ""
    echo "Please restart your Mac to complete the removal."
else
    echo -e "${YELLOW}Driver not found at $KEXT_PATH${NC}"
fi
EOF

    chmod +x "$UNINSTALL_SCRIPT"
    print_success "Created uninstall script: $UNINSTALL_SCRIPT"
}

# Main installation flow
main() {
    print_header
    
    check_macos
    check_sip
    check_homebrew
    check_xcode_tools
    install_dependencies
    clone_driver_source
    configure_build
    build_driver
    sign_driver
    install_driver
    create_uninstall_script
    post_install_instructions
}

# Run main function
main
