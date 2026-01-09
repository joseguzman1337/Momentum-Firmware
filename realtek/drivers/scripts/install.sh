#!/bin/bash

# RTL88xxAU macOS Driver - Modern DriverKit Installer
# This script wraps the new Makefile build system.

set -e

# Colors for output
BLUE='\033[0;34m'
GREEN='\033[0;32m'
NC='\033[0m'

echo -e "${BLUE}[INFO]${NC} minimal maintenance wrapper for RTL88xxAU DriverKit..."

# Ensure we are in the drivers directory (parent of scripts/)
cd "$(dirname "$0")/.."

echo -e "${BLUE}[INFO]${NC} Cleaning previous builds..."
make clean

echo -e "${BLUE}[INFO]${NC} Building and Installing DriverKit App..."

if [ -n "$SUDO_USER" ]; then
    echo -e "${BLUE}[INFO]${NC} Running build as user '$SUDO_USER' for keychain access..."
    # Run 'make install' as the original user
    # This ensures codesign can access the login keychain
    sudo -u "$SUDO_USER" make install
else
    echo -e "${BLUE}[INFO]${NC} SUDO_USER not detected. Running as current user..."
    make install
fi

echo -e "${GREEN}[SUCCESS]${NC} Installer App launched."
echo -e "${BLUE}[INFO]${NC} Please follow the prompts in the 'RTLLoader' app to activate the driver."
echo -e "${BLUE}[INFO]${NC} Check 'System Settings > Privacy & Security' to approve the extension."
