# RTL8814AU macOS Driver

A fully open-source driver for Realtek RTL8814AU USB WiFi adapters for macOS Sequoia with SIP enabled.

## Overview

This driver uses Apple's modern DriverKit framework instead of deprecated kernel extensions, ensuring compatibility with System Integrity Protection (SIP) and modern macOS security requirements.

## Architecture

- **DriverKit Extension**: Userspace driver using IOKit's modern DriverKit framework
- **Network Extension**: System extension for network packet handling
- **USB Communication**: Direct USB communication via IOUSBHostDevice
- **Code Signing**: Properly signed with Apple Developer ID for distribution

## Requirements

- macOS Sequoia (15.0+)
- Xcode 16.0+
- Apple Developer Account (for code signing)
- Homebrew (for dependency management)
- Swift 6.0+

## Building from Source

### 1. Install Dependencies via Homebrew

```bash
# Install build tools
brew install swift
brew install cmake
brew install git

# Clone the repository (if not already done)
# git clone https://github.com/yourusername/rtl8814au-macos-driver
# cd rtl8814au-macos-driver
```

### 2. Configure Code Signing

Edit `CodeSigning.xcconfig` with your Apple Developer Team ID:

```
DEVELOPMENT_TEAM = YOUR_TEAM_ID
```

### 3. Build the Driver

```bash
./build.sh
```

Or manually with Xcode:

```bash
xcodebuild -project RTL8814AUDriver.xcodeproj \
           -scheme RTL8814AUDriver \
           -configuration Release \
           build
```

### 4. Install the Driver

```bash
sudo ./install.sh
```

## Installation

### Automated Installation

```bash
# Download and run the installer
curl -fsSL https://raw.githubusercontent.com/yourusername/rtl8814au-macos-driver/main/install.sh | bash
```

### Manual Installation

1. Download the latest release from the Releases page
2. Extract the archive
3. Run the installer:
   ```bash
   sudo installer -pkg RTL8814AUDriver.pkg -target /
   ```
4. Approve the system extension in System Settings > Privacy & Security
5. Reboot (may be required)

## Usage

Once installed, the driver automatically handles RTL8814AU devices when plugged in. The adapter will appear in System Settings > Network as a standard WiFi interface.

## Uninstallation

```bash
sudo ./uninstall.sh
```

## Troubleshoading

### Driver Not Loading

1. Check System Settings > Privacy & Security for extension approval requests
2. Verify code signature: `codesign -vvv /Library/SystemExtensions/...`
3. Check system logs: `log show --predicate 'subsystem == "com.rtl8814au.driver"' --last 1h`

### USB Device Not Recognized

```bash
# Check if device is detected
ioreg -p IOUSB -l -w 0 | grep -i realtek

# Check USB vendor/product ID (should be 0bda:8813 or similar)
system_profiler SPUSBDataType
```

### Network Issues

```bash
# Check interface status
ifconfig

# Check driver logs
log show --predicate 'subsystem CONTAINS "rtl8814au"' --last 10m --info
```

## Technical Details

### Supported Hardware

- Realtek RTL8814AU chipset
- USB Vendor ID: 0x0bda
- USB Product IDs: 0x8813, 0x8814

### Network Standards

- 802.11a/b/g/n/ac
- Dual-band (2.4GHz and 5GHz)
- Up to 1733 Mbps on 5GHz (4x4 MIMO)
- Up to 800 Mbps on 2.4GHz

### macOS Integration

- Uses DriverKit (not deprecated KEXT)
- Fully compatible with SIP enabled
- Signed and notarized for distribution
- Supports native macOS WiFi menu
- Airport utility compatible

## Development

### Project Structure

```
.
├── RTL8814AUDriver/          # Main driver implementation
│   ├── Driver.swift          # DriverKit driver entry point
│   ├── USBInterface.swift    # USB communication layer
│   ├── WiFiInterface.swift   # WiFi protocol implementation
│   └── Info.plist            # Driver configuration
├── RTL8814AUApp/             # Helper app for installation
│   └── main.swift            # System extension activation
├── Shared/                   # Shared code between driver and app
│   ├── Constants.swift       # Hardware constants
│   └── RTL8814AU.swift       # Chip-specific logic
├── Tests/                    # Unit and integration tests
├── build.sh                  # Build automation script
├── install.sh                # Installation script
└── uninstall.sh              # Uninstallation script
```

### Building for Development

```bash
# Build debug version
xcodebuild -project RTL8814AUDriver.xcodeproj \
           -scheme RTL8814AUDriver \
           -configuration Debug \
           build

# Run tests
xcodebuild test -project RTL8814AUDriver.xcodeproj \
                -scheme RTL8814AUDriverTests
```

### Debugging

```bash
# Enable driver debug logging
sudo log config --mode "level:debug" --subsystem com.rtl8814au.driver

# Monitor driver in real-time
log stream --predicate 'subsystem == "com.rtl8814au.driver"'
```

## Contributing

Contributions are welcome! Please read CONTRIBUTING.md for guidelines.

## License

This project is licensed under the GPL-2.0 License - see LICENSE file for details.

This is an independent open-source project and is not affiliated with or endorsed by Realtek Semiconductor Corp. or Apple Inc.

## Credits

- Based on Realtek's reference driver implementation
- USB layer inspired by open-source RTL8812AU drivers
- Community contributions and testing

## Support

- GitHub Issues: https://github.com/yourusername/rtl8814au-macos-driver/issues
- Discussions: https://github.com/yourusername/rtl8814au-macos-driver/discussions

## Changelog

See CHANGELOG.md for version history.
