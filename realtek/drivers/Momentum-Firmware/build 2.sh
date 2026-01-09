#!/bin/bash

# RTL8814AU Driver Build Script
# Builds the DriverKit extension with proper signing

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
PROJECT_NAME="RTL8814AUDriver"
SCHEME="RTL8814AUDriver"
CONFIGURATION="Release"
BUILD_DIR="build"
DERIVED_DATA="DerivedData"

# Code signing (update these with your values)
SIGNING_IDENTITY="${CODESIGN_IDENTITY:-Developer ID Application}"
TEAM_ID="${TEAM_ID:-YOUR_TEAM_ID}"

echo -e "${GREEN}================================${NC}"
echo -e "${GREEN}RTL8814AU Driver Build Script${NC}"
echo -e "${GREEN}================================${NC}"
echo ""

# Check for Xcode
if ! command -v xcodebuild &> /dev/null; then
    echo -e "${RED}Error: xcodebuild not found. Please install Xcode.${NC}"
    exit 1
fi

echo -e "${YELLOW}Checking Xcode version...${NC}"
xcodebuild -version

# Check for required tools
echo -e "${YELLOW}Checking for required tools...${NC}"
if ! command -v codesign &> /dev/null; then
    echo -e "${RED}Error: codesign not found${NC}"
    exit 1
fi

# Clean previous build
echo -e "${YELLOW}Cleaning previous build...${NC}"
if [ -d "$BUILD_DIR" ]; then
    rm -rf "$BUILD_DIR"
fi

if [ -d "$DERIVED_DATA" ]; then
    rm -rf "$DERIVED_DATA"
fi

# Create directories
mkdir -p "$BUILD_DIR"

# Build the driver
echo -e "${YELLOW}Building driver extension...${NC}"
xcodebuild \
    -project "${PROJECT_NAME}.xcodeproj" \
    -scheme "$SCHEME" \
    -configuration "$CONFIGURATION" \
    -derivedDataPath "$DERIVED_DATA" \
    CODE_SIGN_IDENTITY="$SIGNING_IDENTITY" \
    DEVELOPMENT_TEAM="$TEAM_ID" \
    CODE_SIGN_STYLE=Manual \
    clean build

if [ $? -ne 0 ]; then
    echo -e "${RED}Build failed!${NC}"
    exit 1
fi

# Find the built .dext
DEXT_PATH=$(find "$DERIVED_DATA" -name "*.dext" -type d | head -n 1)

if [ -z "$DEXT_PATH" ]; then
    echo -e "${RED}Error: Could not find built .dext file${NC}"
    exit 1
fi

echo -e "${GREEN}Built driver at: $DEXT_PATH${NC}"

# Copy to build directory
cp -R "$DEXT_PATH" "$BUILD_DIR/"
DEXT_NAME=$(basename "$DEXT_PATH")

echo -e "${YELLOW}Verifying code signature...${NC}"
codesign -vvv --deep --strict "$BUILD_DIR/$DEXT_NAME"

if [ $? -ne 0 ]; then
    echo -e "${RED}Warning: Code signature verification failed${NC}"
else
    echo -e "${GREEN}Code signature verified successfully${NC}"
fi

# Display entitlements
echo -e "${YELLOW}Checking entitlements...${NC}"
codesign -d --entitlements :- "$BUILD_DIR/$DEXT_NAME"

# Create distribution package
echo -e "${YELLOW}Creating distribution package...${NC}"
DIST_DIR="$BUILD_DIR/Distribution"
mkdir -p "$DIST_DIR"

cp -R "$BUILD_DIR/$DEXT_NAME" "$DIST_DIR/"
cp README.md "$DIST_DIR/" 2>/dev/null || true

# Create installer script
cat > "$DIST_DIR/install.sh" << 'EOF'
#!/bin/bash

# RTL8814AU Driver Installation Script

set -e

if [ "$EUID" -ne 0 ]; then
    echo "Please run as root (use sudo)"
    exit 1
fi

DEXT_NAME="RTL8814AUDriver.dext"
INSTALL_PATH="/Library/SystemExtensions"

echo "Installing RTL8814AU Driver..."

# Copy driver to system extensions directory
echo "Copying driver to $INSTALL_PATH..."
cp -R "$DEXT_NAME" "$INSTALL_PATH/"

# Set proper permissions
chmod -R 755 "$INSTALL_PATH/$DEXT_NAME"

echo ""
echo "Driver installed successfully!"
echo ""
echo "IMPORTANT: You must now:"
echo "1. Go to System Settings → Privacy & Security"
echo "2. Allow the system extension when prompted"
echo "3. Restart your Mac"
echo "4. Connect your RTL8814AU device"
echo ""
EOF

chmod +x "$DIST_DIR/install.sh"

# Create archive
echo -e "${YELLOW}Creating distribution archive...${NC}"
cd "$BUILD_DIR"
tar -czf "RTL8814AUDriver-${CONFIGURATION}.tar.gz" Distribution/
cd ..

echo ""
echo -e "${GREEN}================================${NC}"
echo -e "${GREEN}Build completed successfully!${NC}"
echo -e "${GREEN}================================${NC}"
echo ""
echo -e "Driver location: ${GREEN}$BUILD_DIR/$DEXT_NAME${NC}"
echo -e "Distribution package: ${GREEN}$BUILD_DIR/RTL8814AUDriver-${CONFIGURATION}.tar.gz${NC}"
echo ""
echo -e "${YELLOW}Next steps:${NC}"
echo "1. Run ./sign.sh to sign the driver (if not already signed)"
echo "2. Run ./install.sh to install the driver"
echo "3. Approve the system extension in System Settings"
echo ""
