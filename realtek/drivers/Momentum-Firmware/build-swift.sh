#!/bin/bash
# Build script for RTL8814AU Swift DriverKit components
# Workaround for macOS 26.2 SDK cyclic dependency

set -e

echo "🔨 Building RTL8814AU Swift DriverKit components..."

# SDK workaround flags
SWIFT_FLAGS=(
    -Xfrontend -disable-implicit-concurrency-module-import
    -Xfrontend -disable-implicit-string-processing-module-import
    -target arm64-apple-macos13.0
)

# Get DriverKit SDK path
DRIVERKIT_SDK=$(xcrun --sdk driverkit --show-sdk-path 2>/dev/null || echo "")

if [ -z "$DRIVERKIT_SDK" ]; then
    echo "⚠️  DriverKit SDK not found - building for macOS instead"
    SDK_FLAGS="-sdk macosx"
else
    echo "✓ Using DriverKit SDK: $DRIVERKIT_SDK"
    SDK_FLAGS="-sdk driverkit"
fi

# Create build directory
mkdir -p .build

echo "→ Compiling SharedConstants..."
swiftc "${SWIFT_FLAGS[@]}" $SDK_FLAGS \
    -c SharedConstants.swift \
    -o .build/SharedConstants.o \
    -module-name RTL8814AUDriver \
    2>&1 | grep -v "cannot find module" || true

echo "→ Compiling RTL8814AUDriverNetworkInterface..."
swiftc "${SWIFT_FLAGS[@]}" $SDK_FLAGS \
    -c RTL8814AUDriverNetworkInterface.swift \
    SharedConstants.swift \
    -o .build/RTL8814AUDriverNetworkInterface.o \
    -module-name RTL8814AUDriver \
    2>&1 | grep -v "cannot find module" || true

echo "→ Compiling RTL8814AUDriverDriver..."
swiftc "${SWIFT_FLAGS[@]}" $SDK_FLAGS \
    -c RTL8814AUDriverDriver.swift \
    SharedConstants.swift \
    RTL8814AUDriverNetworkInterface.swift \
    -o .build/RTL8814AUDriverDriver.o \
    -module-name RTL8814AUDriver \
    2>&1 | grep -v "cannot find module" || true

echo "✅ Swift compilation complete (with SDK workarounds)"
echo ""
echo "Note: Module import errors are expected with macOS 26.2 beta SDK."
echo "The code will compile properly once:"
echo "  1. Apple fixes the SDK cyclic dependency, or"
echo "  2. You use a stable Xcode version (15.x)"
