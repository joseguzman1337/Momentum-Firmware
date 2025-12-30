#!/bin/bash

# RTL8814AU Driver - Quick Setup Script
# This script automates the initial setup and installation

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Configuration
REQUIRED_MACOS_VERSION="15.0"
REQUIRED_XCODE_VERSION="16.0"

echo -e "${BLUE}"
echo "╔═══════════════════════════════════════════════════════════╗"
echo "║                                                           ║"
echo "║         RTL8814AU Driver for macOS Sequoia               ║"
echo "║                  Quick Setup Script                       ║"
echo "║                                                           ║"
echo "╚═══════════════════════════════════════════════════════════╝"
echo -e "${NC}"
echo ""

# Function to check command existence
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to compare versions
version_compare() {
    if [[ "$1" == "$2" ]]; then
        return 0
    fi
    local IFS=.
    local i ver1=($1) ver2=($2)
    for ((i=${#ver1[@]}; i<${#ver2[@]}; i++)); do
        ver1[i]=0
    done
    for ((i=0; i<${#ver1[@]}; i++)); do
        if [[ -z ${ver2[i]} ]]; then
            ver2[i]=0
        fi
        if ((10#${ver1[i]} > 10#${ver2[i]})); then
            return 1
        fi
        if ((10#${ver1[i]} < 10#${ver2[i]})); then
            return 2
        fi
    done
    return 0
}

# Check macOS version
echo -e "${YELLOW}Checking system requirements...${NC}"
MACOS_VERSION=$(sw_vers -productVersion)
echo "macOS version: $MACOS_VERSION"

version_compare "$MACOS_VERSION" "$REQUIRED_MACOS_VERSION"
if [[ $? -eq 2 ]]; then
    echo -e "${RED}Error: This driver requires macOS $REQUIRED_MACOS_VERSION or later${NC}"
    echo "Your version: $MACOS_VERSION"
    exit 1
fi

# Check SIP status
echo ""
echo -e "${YELLOW}Checking System Integrity Protection (SIP)...${NC}"
SIP_STATUS=$(csrutil status)
echo "$SIP_STATUS"

if echo "$SIP_STATUS" | grep -q "disabled"; then
    echo -e "${YELLOW}⚠️  Warning: SIP is disabled${NC}"
    echo "This driver is designed to work WITH SIP enabled."
    echo "It is recommended to enable SIP for better security."
    echo ""
    read -p "Do you want to continue anyway? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
else
    echo -e "${GREEN}✓ SIP is enabled (recommended)${NC}"
fi

# Check for Xcode
echo ""
echo -e "${YELLOW}Checking for Xcode...${NC}"
if command_exists xcodebuild; then
    XCODE_VERSION=$(xcodebuild -version | head -n 1 | awk '{print $2}')
    echo "Xcode version: $XCODE_VERSION"
    
    version_compare "$XCODE_VERSION" "$REQUIRED_XCODE_VERSION"
    if [[ $? -eq 2 ]]; then
        echo -e "${YELLOW}⚠️  Warning: Xcode $REQUIRED_XCODE_VERSION or later is recommended${NC}"
        echo "Your version: $XCODE_VERSION"
    else
        echo -e "${GREEN}✓ Xcode version is compatible${NC}"
    fi
else
    echo -e "${RED}✗ Xcode not found${NC}"
    echo ""
    echo "Please install Xcode from the App Store or run:"
    echo "  xcode-select --install"
    exit 1
fi

# Check for Homebrew
echo ""
echo -e "${YELLOW}Checking for Homebrew...${NC}"
if command_exists brew; then
    echo -e "${GREEN}✓ Homebrew is installed${NC}"
    BREW_VERSION=$(brew --version | head -n 1)
    echo "$BREW_VERSION"
else
    echo -e "${YELLOW}○ Homebrew not found${NC}"
    echo ""
    read -p "Would you like to install Homebrew? (Y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Nn]$ ]]; then
        echo "Installing Homebrew..."
        /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    fi
fi

# Check for development tools
echo ""
echo -e "${YELLOW}Checking optional development tools...${NC}"

if command_exists swiftlint; then
    echo -e "${GREEN}✓ SwiftLint${NC}"
else
    echo -e "${YELLOW}○ SwiftLint not found (optional)${NC}"
    read -p "Install SwiftLint for code quality checks? (y/N) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        brew install swiftlint
    fi
fi

if command_exists swift-format; then
    echo -e "${GREEN}✓ swift-format${NC}"
else
    echo -e "${YELLOW}○ swift-format not found (optional)${NC}"
    read -p "Install swift-format for code formatting? (y/N) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        brew install swift-format
    fi
fi

# Check for Apple Developer setup
echo ""
echo -e "${YELLOW}Checking code signing setup...${NC}"
SIGNING_IDENTITIES=$(security find-identity -v -p codesigning | grep "Developer ID" || true)

if [ -z "$SIGNING_IDENTITIES" ]; then
    echo -e "${YELLOW}⚠️  No Developer ID certificate found${NC}"
    echo ""
    echo "To build and install this driver, you need:"
    echo "  1. An Apple Developer account"
    echo "  2. A 'Developer ID Application' certificate"
    echo ""
    echo "For development/testing only, you can enable developer mode:"
    echo "  sudo systemextensionsctl developer on"
    echo ""
    read -p "Continue without certificate? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
else
    echo -e "${GREEN}✓ Developer ID certificate found${NC}"
    echo "$SIGNING_IDENTITIES"
fi

# Make scripts executable
echo ""
echo -e "${YELLOW}Setting up build scripts...${NC}"
chmod +x build.sh sign.sh install.sh 2>/dev/null || true
echo -e "${GREEN}✓ Scripts are executable${NC}"

# Summary and next steps
echo ""
echo -e "${GREEN}╔═══════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║                 Setup Complete! ✓                        ║${NC}"
echo -e "${GREEN}╚═══════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${BLUE}What to do next:${NC}"
echo ""
echo "1. ${YELLOW}Configure code signing${NC}"
echo "   Edit these files and add your Team ID:"
echo "   - ${GREEN}Makefile${NC} (line: TEAM_ID)"
echo "   - ${GREEN}build.sh${NC} (line: TEAM_ID)"
echo "   - ${GREEN}sign.sh${NC} (line: TEAM_ID)"
echo ""
echo "2. ${YELLOW}Build the driver${NC}"
echo "   ${GREEN}make build${NC}"
echo "   or"
echo "   ${GREEN}./build.sh${NC}"
echo ""
echo "3. ${YELLOW}Sign the driver${NC} (requires Developer ID)"
echo "   ${GREEN}make sign${NC}"
echo "   or"
echo "   ${GREEN}./sign.sh${NC}"
echo ""
echo "4. ${YELLOW}Install the driver${NC} (requires sudo)"
echo "   ${GREEN}sudo make install${NC}"
echo "   or"
echo "   ${GREEN}sudo ./install.sh${NC}"
echo ""
echo "5. ${YELLOW}Approve in System Settings${NC}"
echo "   - Open System Settings → Privacy & Security"
echo "   - Scroll to Security section"
echo "   - Click 'Allow' for the RTL8814AU Driver"
echo ""
echo "6. ${YELLOW}Restart your Mac${NC}"
echo ""
echo "7. ${YELLOW}Connect your RTL8814AU device${NC}"
echo ""
echo -e "${BLUE}Quick commands:${NC}"
echo "  ${GREEN}make help${NC}          - Show all available commands"
echo "  ${GREEN}make status${NC}        - Check driver status"
echo "  ${GREEN}make logs${NC}          - View driver logs"
echo "  ${GREEN}make dev-mode-on${NC}   - Enable developer mode (testing)"
echo ""
echo -e "${BLUE}Documentation:${NC}"
echo "  ${GREEN}README.md${NC}         - Project overview"
echo "  ${GREEN}BUILDING.md${NC}       - Detailed build instructions"
echo "  ${GREEN}CONTRIBUTING.md${NC}   - Contribution guidelines"
echo ""
echo -e "${YELLOW}For development without full signing:${NC}"
echo "  ${GREEN}sudo systemextensionsctl developer on${NC}"
echo "  ${GREEN}make build install${NC}"
echo ""
echo -e "${BLUE}Need help?${NC}"
echo "  GitHub Issues: https://github.com/yourusername/rtl8814au-macos/issues"
echo "  Documentation: https://github.com/yourusername/rtl8814au-macos/wiki"
echo ""
echo -e "${GREEN}Ready to build! Good luck! 🚀${NC}"
echo ""
