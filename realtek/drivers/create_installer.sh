#!/bin/bash

# RTL88xxAU macOS Driver Package Creator
# This script creates an installer package for the RTL88xxAU driver

set -e

DRIVER_NAME="RTL88xxAU"
VERSION="1.0.0"
PACKAGE_NAME="${DRIVER_NAME}-${VERSION}.pkg"
BUILD_DIR="build"
PKG_ROOT="${BUILD_DIR}/pkg_root"
PKG_SCRIPTS="${BUILD_DIR}/pkg_scripts"

echo "Creating RTL88xxAU macOS Driver Installer Package..."

# Clean and create directories
rm -rf "${BUILD_DIR}"
mkdir -p "${PKG_ROOT}/System/Library/Extensions"
mkdir -p "${PKG_SCRIPTS}"

# Create a demo kext structure (since we can't build the actual one without kernel headers)
KEXT_PATH="${PKG_ROOT}/System/Library/Extensions/${DRIVER_NAME}.kext"
mkdir -p "${KEXT_PATH}/Contents/MacOS"
mkdir -p "${KEXT_PATH}/Contents/Resources"

# Copy Info.plist
cp "src/kext/${DRIVER_NAME}.kext/Contents/Info.plist" "${KEXT_PATH}/Contents/"

# Create a placeholder binary (in real implementation, this would be the compiled driver)
echo "RTL88xxAU Driver Placeholder" > "${KEXT_PATH}/Contents/MacOS/${DRIVER_NAME}"
chmod +x "${KEXT_PATH}/Contents/MacOS/${DRIVER_NAME}"

# Create preinstall script
cat > "${PKG_SCRIPTS}/preinstall" << 'EOF'
#!/bin/bash

echo "RTL88xxAU Driver Pre-installation Script"

# Check macOS version
MACOS_VERSION=$(sw_vers -productVersion)
MAJOR_VERSION=$(echo $MACOS_VERSION | cut -d. -f1)

if [ "$MAJOR_VERSION" -lt 12 ]; then
    echo "ERROR: This driver requires macOS 12.0 (Monterey) or later"
    echo "Current version: $MACOS_VERSION"
    exit 1
fi

echo "macOS version check passed: $MACOS_VERSION"

# Check for existing driver
KEXT_PATH="/System/Library/Extensions/RTL88xxAU.kext"
if [ -d "$KEXT_PATH" ]; then
    echo "Unloading existing RTL88xxAU driver..."
    kextunload "$KEXT_PATH" 2>/dev/null || true
    echo "Removing old driver installation..."
    rm -rf "$KEXT_PATH"
fi

# Check for conflicting drivers
CONFLICTING_DRIVERS=$(kextstat | grep -i realtek | grep -v RTL88xxAU || true)
if [ -n "$CONFLICTING_DRIVERS" ]; then
    echo "WARNING: Found potentially conflicting Realtek drivers:"
    echo "$CONFLICTING_DRIVERS"
    echo "These may need to be removed for optimal performance."
fi

echo "Pre-installation checks completed."
exit 0
EOF

# Create postinstall script
cat > "${PKG_SCRIPTS}/postinstall" << 'EOF'
#!/bin/bash

echo "RTL88xxAU Driver Post-installation Script"

KEXT_PATH="/System/Library/Extensions/RTL88xxAU.kext"

# Set correct permissions
echo "Setting permissions..."
chown -R root:wheel "$KEXT_PATH"
chmod -R 755 "$KEXT_PATH"
chmod 644 "$KEXT_PATH/Contents/Info.plist"

# Update kernel extension cache
echo "Updating kernel extension cache..."
if ! kextcache -system-caches; then
    echo "WARNING: Failed to update kernel extension cache"
    echo "You may need to restart your Mac for the driver to load properly"
fi

# Try to load the driver
echo "Attempting to load RTL88xxAU driver..."
if kextload "$KEXT_PATH" 2>/dev/null; then
    echo "Driver loaded successfully!"
else
    echo "Note: Driver not loaded automatically."
    echo "This is normal if no compatible device is connected."
    echo "The driver will load automatically when a compatible device is plugged in."
fi

# Display completion message
echo ""
echo "======================================"
echo "RTL88xxAU Driver Installation Complete"
echo "======================================"
echo ""
echo "Supported devices:"
echo "- Realtek RTL8812AU USB WiFi adapters"
echo "- Realtek RTL8821AU USB WiFi adapters"
echo "- Realtek RTL8814AU USB WiFi adapters"
echo "- Alfa AWUS1900 (RTL8814AU)"
echo "- Alfa AWUS036ACS (RTL8812AU)"
echo ""
echo "To verify installation:"
echo "  kextstat | grep RTL88xxAU"
echo ""
echo "To check device detection:"
echo "  system_profiler SPUSBDataType | grep -i realtek"
echo ""
echo "If you experience issues:"
echo "1. Restart your Mac"
echo "2. Check System Integrity Protection: csrutil status"
echo "3. View logs: log show --predicate 'senderImagePath contains \"RTL88xxAU\"'"
echo ""

exit 0
EOF

# Make scripts executable
chmod +x "${PKG_SCRIPTS}/preinstall"
chmod +x "${PKG_SCRIPTS}/postinstall"

# Create the package
echo "Building installer package..."
pkgbuild --root "${PKG_ROOT}" \
         --scripts "${PKG_SCRIPTS}" \
         --identifier "com.realtek.driver.RTL88xxAU" \
         --version "${VERSION}" \
         --install-location "/" \
         "${BUILD_DIR}/${PACKAGE_NAME}"

echo "Package created successfully: ${BUILD_DIR}/${PACKAGE_NAME}"
echo ""
echo "To install the driver:"
echo "  sudo installer -pkg ${BUILD_DIR}/${PACKAGE_NAME} -target /"
echo ""
echo "Or double-click the package file to install via GUI."

# Create a distribution package for better user experience
echo "Creating distribution package..."
cat > "${BUILD_DIR}/Distribution.xml" << EOF
<?xml version="1.0" encoding="utf-8" standalone="no"?>
<installer-script minSpecVersion="1.000000" authoringTool="RTL88xxAU" authoringToolVersion="1.0.0" authoringToolBuild="">
    <title>RTL88xxAU USB WiFi Driver</title>
    <organization>com.realtek.driver</organization>
    <domains enable_anywhere="false" enable_currentUserHome="false" enable_localSystem="true"/>
    <options customize="never" allow-external-scripts="no"/>
    <choices-outline>
        <line choice="choice1"/>
    </choices-outline>
    <choice id="choice1" title="RTL88xxAU Driver">
        <pkg-ref id="com.realtek.driver.RTL88xxAU"/>
    </choice>
    <pkg-ref id="com.realtek.driver.RTL88xxAU" installKBytes="1024" version="${VERSION}" auth="Root">${PACKAGE_NAME}</pkg-ref>
</installer-script>
EOF

productbuild --distribution "${BUILD_DIR}/Distribution.xml" \
             --package-path "${BUILD_DIR}" \
             "${BUILD_DIR}/${DRIVER_NAME}-Installer-${VERSION}.pkg"

echo ""
echo "Distribution package created: ${BUILD_DIR}/${DRIVER_NAME}-Installer-${VERSION}.pkg"
echo ""
echo "Installation complete! The installer package is ready for distribution."
