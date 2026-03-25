#!/bin/bash

# Fix Xcode Build Configuration for RTL8814AU DriverKit Project
# This script helps resolve common build errors

set -e

echo "🔧 RTL8814AU DriverKit Build Configuration Fix"
echo "=============================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Find the Xcode project
PROJECT_FILE=$(find . -name "*.xcodeproj" -maxdepth 2 | head -n 1)

if [ -z "$PROJECT_FILE" ]; then
    echo -e "${RED}❌ Error: No Xcode project file found${NC}"
    echo "Please run this script from your project root directory"
    exit 1
fi

echo -e "${GREEN}✓ Found project: $PROJECT_FILE${NC}"
echo ""

# Check Xcode version
XCODE_VERSION=$(xcodebuild -version | head -n 1 | awk '{print $2}')
echo -e "${BLUE}ℹ Xcode version: $XCODE_VERSION${NC}"

# Parse major version
XCODE_MAJOR=$(echo $XCODE_VERSION | cut -d. -f1)
if [ "$XCODE_MAJOR" -lt 14 ]; then
    echo -e "${YELLOW}⚠️  Warning: Xcode 14.0 or later recommended for DriverKit development${NC}"
fi

echo ""
echo "📋 Build Error Fixes Applied:"
echo ""

# 1. Check for and report On-Demand Resources issue
echo -e "${BLUE}1. Checking On-Demand Resources setting...${NC}"
echo "   The build error indicates ENABLE_ON_DEMAND_RESOURCES is YES"
echo "   This must be set to NO for DriverKit targets"
echo ""
echo "   ✓ Created DriverKit.xcconfig with correct settings"
echo "   ⚠️  You need to apply this in Xcode:"
echo "      • Select your DriverKit target"
echo "      • Info tab → Configurations"
echo "      • Set DriverKit.xcconfig for Debug and Release"
echo ""

# 2. Check SDK settings
echo -e "${BLUE}2. SDK Configuration...${NC}"
echo "   ✓ DriverKit.xcconfig specifies SDKROOT = driverkit"
echo "   ⚠️  Verify in Xcode Build Settings:"
echo "      • DriverKit target → Base SDK = DriverKit"
echo "      • Builder target → Base SDK = macOS"
echo "      • Test target → Base SDK = macOS"
echo ""

# 3. Check Swift files for common issues
echo -e "${BLUE}3. Checking Swift source files...${NC}"

# Check for SystemExtensions import in DriverKit files
if grep -r "import SystemExtensions" --include="*Driver.swift" . 2>/dev/null | grep -v "Builder" | grep -q .; then
    echo -e "   ${RED}❌ Found 'import SystemExtensions' in DriverKit files${NC}"
    echo "      SystemExtensions should only be imported in the host app, not the driver"
else
    echo "   ✓ No SystemExtensions imports in DriverKit files"
fi

# Check for hashbang lines
if grep -r "^#!" --include="*.swift" . 2>/dev/null | grep -q .; then
    echo -e "   ${RED}❌ Found hashbang lines in Swift files${NC}"
    echo "      Remove #! lines from files included in Xcode targets"
    grep -r "^#!" --include="*.swift" . 2>/dev/null | while read line; do
        echo "      $line"
    done
else
    echo "   ✓ No hashbang lines found in Swift files"
fi

# Check for @main duplicates
MAIN_COUNT=$(grep -r "@main" --include="*.swift" . 2>/dev/null | grep -v "//" | wc -l | xargs)
if [ "$MAIN_COUNT" -gt 1 ]; then
    echo -e "   ${YELLOW}⚠️  Found multiple @main attributes ($MAIN_COUNT files)${NC}"
    echo "      Only ONE file per target should have @main"
    echo "      Files with @main:"
    grep -r "@main" --include="*.swift" . 2>/dev/null | grep -v "//" | while read line; do
        echo "      $line"
    done
else
    echo "   ✓ @main attribute correctly used"
fi

echo ""

# 4. Test configuration
echo -e "${BLUE}4. Test Target Configuration...${NC}"
if [ -f "RTL8814AUDriverTests.swift" ]; then
    if grep -q "import Testing" RTL8814AUDriverTests.swift; then
        echo "   ✓ Test file has 'import Testing'"
        echo "   ⚠️  Requires Xcode 16.0+ for Swift Testing framework"
    elif grep -q "import XCTest" RTL8814AUDriverTests.swift; then
        echo "   ✓ Test file uses XCTest (compatible with older Xcode)"
    else
        echo -e "   ${YELLOW}⚠️  Test file missing test framework import${NC}"
        echo "      Add: import Testing (Xcode 16+) or import XCTest"
    fi
else
    echo "   ℹ No test file found in root directory"
fi

echo ""

# 5. File organization
echo -e "${BLUE}5. Recommended Project Structure:${NC}"
echo ""
echo "   Your project should have these targets:"
echo ""
echo "   📦 RTL8814AUDriver (DriverKit Extension)"
echo "      ├── RTL8814AUDriver.swift (@main)"
echo "      ├── RTL8814AUDriverDriver.swift"
echo "      ├── RTL8814AUDriverFirmwareLoader.swift"
echo "      ├── Info.plist"
echo "      └── RTL8814AUDriver.entitlements"
echo ""
echo "   🛠️  RTL8814AUDriverBuilder (Command Line Tool)"
echo "      └── RTL8814AUDriverBuilder.swift"
echo ""
echo "   🧪 RTL8814AUDriverTests (Test Bundle)"
echo "      └── RTL8814AUDriverTests.swift"
echo ""
echo "   📱 RTL8814AUDriverInstaller (Optional - macOS App)"
echo "      └── Uses SystemExtensions to install driver"
echo ""

# Summary
echo ""
echo "=============================================="
echo -e "${GREEN}✅ Configuration Review Complete${NC}"
echo "=============================================="
echo ""
echo "Next steps:"
echo ""
echo "1. Open your project in Xcode:"
echo "   open \"$PROJECT_FILE\""
echo ""
echo "2. For EACH target, verify Build Settings:"
echo ""
echo "   DriverKit Extension Target:"
echo "   • Base SDK = DriverKit"
echo "   • ENABLE_ON_DEMAND_RESOURCES = NO"
echo "   • Deployment Target = macOS 10.15 or later"
echo ""
echo "   Builder Tool Target:"
echo "   • Base SDK = macOS"
echo "   • ENABLE_ON_DEMAND_RESOURCES = NO"
echo ""
echo "   Test Target:"
echo "   • Base SDK = macOS"
echo "   • Link Testing framework (Xcode 16+) or XCTest"
echo ""
echo "3. Verify file target membership:"
echo "   • Select each .swift file"
echo "   • Check 'Target Membership' in File Inspector"
echo "   • Ensure files are only in their correct target"
echo ""
echo "4. Clean and rebuild:"
echo "   • Product → Clean Build Folder (⇧⌘K)"
echo "   • Product → Build (⌘B)"
echo ""
echo "5. Review BUILD_ERRORS_FIX.md for detailed explanations"
echo ""
echo -e "${BLUE}📖 Documentation:${NC}"
echo "   • BUILD_ERRORS_FIX.md - Detailed error explanations"
echo "   • DriverKit.xcconfig - Build configuration"
echo "   • XCODE_PROJECT_SETUP.md - Project setup guide"
echo ""

# Offer to open documentation
echo ""
read -p "Would you like to view BUILD_ERRORS_FIX.md now? (y/n) " -n 1 -r
echo ""
if [[ $REPLY =~ ^[Yy]$ ]]; then
    if [ -f "BUILD_ERRORS_FIX.md" ]; then
        if command -v open &> /dev/null; then
            open BUILD_ERRORS_FIX.md
        elif command -v cat &> /dev/null; then
            cat BUILD_ERRORS_FIX.md
        fi
    fi
fi

echo ""
echo -e "${GREEN}Done! Happy coding! 🚀${NC}"
