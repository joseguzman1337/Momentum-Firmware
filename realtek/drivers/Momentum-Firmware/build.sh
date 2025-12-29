#!/bin/bash
set -e

echo "🔨 Building RTL8814AU Driver for macOS Sequoia..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if running on macOS
if [[ "$(uname)" != "Darwin" ]]; then
    echo -e "${RED}Error: This script must be run on macOS${NC}"
    exit 1
fi

# Check macOS version (require Sequoia 15.0+)
MACOS_VERSION=$(sw_vers -productVersion | cut -d '.' -f 1)
if [[ $MACOS_VERSION -lt 15 ]]; then
    echo -e "${RED}Error: macOS Sequoia (15.0) or later is required${NC}"
    exit 1
fi

# Check if Xcode is installed
if ! command -v xcodebuild &> /dev/null; then
    echo -e "${RED}Error: Xcode is not installed. Please install Xcode from the App Store.${NC}"
    exit 1
fi

# Check Xcode version
XCODE_VERSION=$(xcodebuild -version | head -n1 | awk '{print $2}' | cut -d '.' -f 1)
if [[ $XCODE_VERSION -lt 16 ]]; then
    echo -e "${YELLOW}Warning: Xcode 16 or later is recommended${NC}"
fi

# Check for code signing configuration
if [[ ! -f "CodeSigning.xcconfig" ]]; then
    echo -e "${YELLOW}Warning: CodeSigning.xcconfig not found. Creating template...${NC}"
    cat > CodeSigning.xcconfig << EOF
// Replace YOUR_TEAM_ID with your Apple Developer Team ID
DEVELOPMENT_TEAM = YOUR_TEAM_ID
CODE_SIGN_IDENTITY = Apple Development
CODE_SIGN_STYLE = Automatic

// For distribution, use:
// CODE_SIGN_IDENTITY = Developer ID Application
EOF
    echo -e "${YELLOW}Please edit CodeSigning.xcconfig with your Team ID before building${NC}"
    exit 1
fi

# Create build directory
BUILD_DIR="build"
mkdir -p "$BUILD_DIR"

echo "📦 Installing Homebrew dependencies..."
if ! command -v brew &> /dev/null; then
    echo -e "${YELLOW}Homebrew not found. Installing...${NC}"
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
fi

# Install required packages via Homebrew
brew list swift &> /dev/null || brew install swift
brew list cmake &> /dev/null || brew install cmake

echo "🧹 Cleaning previous build..."
xcodebuild clean -project RTL8814AUDriver.xcodeproj -scheme RTL8814AUDriver -configuration Release &> /dev/null || true

echo "🔨 Building driver..."
xcodebuild -project RTL8814AUDriver.xcodeproj \
           -scheme RTL8814AUDriver \
           -configuration Release \
           -derivedDataPath "$BUILD_DIR/DerivedData" \
           build

if [[ $? -eq 0 ]]; then
    echo -e "${GREEN}✅ Build successful!${NC}"
    
    # Find built products
    DRIVER_PATH=$(find "$BUILD_DIR/DerivedData" -name "*.dext" -type d | head -n 1)
    APP_PATH=$(find "$BUILD_DIR/DerivedData" -name "RTL8814AUApp.app" -type d | head -n 1)
    
    if [[ -n "$DRIVER_PATH" ]]; then
        echo -e "${GREEN}Driver built at: $DRIVER_PATH${NC}"
        
        # Verify code signature
        echo "🔐 Verifying code signature..."
        codesign -vvv --deep --strict "$DRIVER_PATH"
        
        if [[ $? -eq 0 ]]; then
            echo -e "${GREEN}✅ Code signature valid${NC}"
        else
            echo -e "${RED}❌ Code signature verification failed${NC}"
            exit 1
        fi
    fi
    
    # Copy to output directory
    OUTPUT_DIR="$BUILD_DIR/Output"
    mkdir -p "$OUTPUT_DIR"
    
    if [[ -n "$DRIVER_PATH" ]]; then
        cp -R "$DRIVER_PATH" "$OUTPUT_DIR/"
        echo -e "${GREEN}Driver copied to $OUTPUT_DIR${NC}"
    fi
    
    if [[ -n "$APP_PATH" ]]; then
        cp -R "$APP_PATH" "$OUTPUT_DIR/"
        echo -e "${GREEN}Helper app copied to $OUTPUT_DIR${NC}"
    fi
    
    echo ""
    echo -e "${GREEN}🎉 Build complete!${NC}"
    echo ""
    echo "Next steps:"
    echo "1. Run './install.sh' to install the driver (requires sudo)"
    echo "2. Approve the system extension in System Settings > Privacy & Security"
    echo "3. Reboot your Mac if prompted"
    
else
    echo -e "${RED}❌ Build failed${NC}"
    exit 1
fi
