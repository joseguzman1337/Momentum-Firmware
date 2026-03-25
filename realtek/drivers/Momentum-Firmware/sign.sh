#!/bin/bash

# RTL8814AU Driver Code Signing Script
# Signs the driver extension with Developer ID for distribution

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}================================${NC}"
echo -e "${GREEN}RTL8814AU Driver Signing Script${NC}"
echo -e "${GREEN}================================${NC}"
echo ""

# Configuration
DEXT_PATH="build/RTL8814AUDriver.dext"
SIGNING_IDENTITY="${CODESIGN_IDENTITY:-Developer ID Application}"
TEAM_ID="${TEAM_ID:-YOUR_TEAM_ID}"

# Check if driver exists
if [ ! -d "$DEXT_PATH" ]; then
    echo -e "${RED}Error: Driver not found at $DEXT_PATH${NC}"
    echo "Please run ./build.sh first"
    exit 1
fi

echo -e "${YELLOW}Checking for signing identity...${NC}"

# List available signing identities
echo "Available signing identities:"
security find-identity -v -p codesigning

echo ""
echo -e "${YELLOW}Using signing identity: $SIGNING_IDENTITY${NC}"
echo -e "${YELLOW}Team ID: $TEAM_ID${NC}"
echo ""

# Remove existing signature
echo -e "${YELLOW}Removing existing signature...${NC}"
codesign --remove-signature "$DEXT_PATH" 2>/dev/null || true

# Sign the driver
echo -e "${YELLOW}Signing driver extension...${NC}"
codesign \
    --sign "$SIGNING_IDENTITY" \
    --force \
    --options runtime \
    --timestamp \
    --deep \
    --entitlements "RTL8814AUDriver/RTL8814AUDriver.entitlements" \
    --identifier "com.opensource.RTL8814AUDriver" \
    "$DEXT_PATH"

if [ $? -ne 0 ]; then
    echo -e "${RED}Signing failed!${NC}"
    exit 1
fi

# Verify signature
echo -e "${YELLOW}Verifying signature...${NC}"
codesign -vvv --deep --strict "$DEXT_PATH"

if [ $? -ne 0 ]; then
    echo -e "${RED}Signature verification failed!${NC}"
    exit 1
fi

echo -e "${GREEN}Signature verified successfully!${NC}"

# Display signature info
echo -e "${YELLOW}Signature details:${NC}"
codesign -dvv "$DEXT_PATH" 2>&1 | grep -E "Authority|Identifier|TeamIdentifier|Timestamp"

# Display entitlements
echo ""
echo -e "${YELLOW}Entitlements:${NC}"
codesign -d --entitlements :- "$DEXT_PATH" 2>/dev/null | grep -A 100 "<dict>"

echo ""
echo -e "${GREEN}================================${NC}"
echo -e "${GREEN}Signing completed successfully!${NC}"
echo -e "${GREEN}================================${NC}"
echo ""

# Check if we should notarize
echo -e "${YELLOW}Do you want to notarize this driver? (y/N)${NC}"
read -r response

if [[ "$response" =~ ^[Yy]$ ]]; then
    echo ""
    echo -e "${YELLOW}Creating ZIP for notarization...${NC}"
    
    ZIP_PATH="build/RTL8814AUDriver.zip"
    cd build
    zip -r "RTL8814AUDriver.zip" "RTL8814AUDriver.dext"
    cd ..
    
    echo -e "${GREEN}ZIP created: $ZIP_PATH${NC}"
    echo ""
    echo -e "${YELLOW}To notarize, run:${NC}"
    echo ""
    echo "xcrun notarytool submit $ZIP_PATH \\"
    echo "  --apple-id YOUR_APPLE_ID \\"
    echo "  --team-id $TEAM_ID \\"
    echo "  --password YOUR_APP_SPECIFIC_PASSWORD \\"
    echo "  --wait"
    echo ""
    echo -e "${YELLOW}After notarization succeeds, staple the ticket:${NC}"
    echo ""
    echo "xcrun stapler staple $DEXT_PATH"
    echo ""
else
    echo ""
    echo -e "${YELLOW}Notarization skipped.${NC}"
    echo -e "${YELLOW}Note: For distribution outside of development, notarization is required.${NC}"
    echo ""
fi

echo -e "${YELLOW}Next steps:${NC}"
echo "1. If notarized, staple the ticket"
echo "2. Run ./install.sh to install the driver"
echo ""
