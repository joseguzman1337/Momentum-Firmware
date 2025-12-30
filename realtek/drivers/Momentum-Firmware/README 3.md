# RTL8814AU Driver for macOS Sequoia

A fully open-source DriverKit-based driver for USB RTL8814AU WiFi adapters compatible with macOS Sequoia with System Integrity Protection (SIP) enabled.

## Overview

This project provides a modern DriverKit implementation for Realtek RTL8814AU USB WiFi adapters, designed to work seamlessly with macOS Sequoia while respecting SIP requirements.

### Key Features

- ✅ **SIP Compatible**: Uses DriverKit instead of deprecated kernel extensions
- ✅ **Apple Signed**: Properly signed and notarized for macOS Sequoia
- ✅ **Homebrew Integration**: Easy installation via brew
- ✅ **Fully Open Source**: Complete source code available
- ✅ **Native Swift Implementation**: Modern Swift-based driver

## System Requirements

- macOS Sequoia (15.0+)
- System Integrity Protection (SIP) enabled
- Xcode 16.0+ (for building from source)
- Homebrew (for installation)

## Supported Hardware

- Realtek RTL8814AU USB WiFi adapters
- Compatible with USB 2.0 and USB 3.0 ports

## Installation

### Quick Install via Homebrew

```bash
# Add the tap
brew tap yourusername/rtl8814au

# Install the driver
brew install --cask rtl8814au-driver

# Approve system extension
sudo systemextensionsctl list
```

### Manual Installation

1. Build the driver:
```bash
xcodebuild -project RTL8814AUDriver.xcodeproj -scheme RTL8814AUDriver -configuration Release
```

2. Install the driver extension:
```bash
sudo cp -R build/Release/RTL8814AUDriver.dext /Library/SystemExtensions/
```

3. Activate the system extension (requires user approval in System Settings)

## Architecture

This driver consists of several components:

1. **DriverKit Extension** (`RTL8814AUDriver.dext`): Main driver logic
2. **Helper App** (`RTL8814AUHelper.app`): Manages driver activation
3. **USB Communication Layer**: Handles USB device communication
4. **Firmware Loader**: Loads RTL8814AU firmware
5. **Network Interface**: Creates virtual network interface

## Building from Source

### Prerequisites

```bash
# Install Xcode Command Line Tools
xcode-select --install

# Install required tools
brew install cmake
brew install swift-format
```

### Build Steps

1. Clone the repository:
```bash
git clone https://github.com/yourusername/rtl8814au-macos.git
cd rtl8814au-macos
```

2. Build the project:
```bash
./build.sh
```

3. Sign the driver (requires valid Apple Developer ID):
```bash
./sign.sh
```

## Code Signing Requirements

To work with SIP enabled, the driver must be properly signed:

1. **Developer ID**: You need an Apple Developer account
2. **Certificates**: "Developer ID Application" certificate
3. **Entitlements**: Proper DriverKit entitlements
4. **Notarization**: Notarized by Apple

### Signing Configuration

The driver uses these entitlements:
- `com.apple.developer.driverkit`
- `com.apple.developer.driverkit.transport.usb`
- `com.apple.developer.networking.networkextension`

## Usage

Once installed, the driver will automatically detect and activate when an RTL8814AU device is connected.

### Check Driver Status

```bash
# List system extensions
systemextensionsctl list

# Check USB devices
system_profiler SPUSBDataType

# Monitor driver logs
log stream --predicate 'subsystem == "com.yourcompany.RTL8814AUDriver"'
```

## Troubleshooting

### Driver Not Loading

1. Ensure SIP is enabled (required for DriverKit):
```bash
csrutil status
```

2. Check for driver approval in System Settings → Privacy & Security

3. Verify code signature:
```bash
codesign -vv -d /Library/SystemExtensions/.../RTL8814AUDriver.dext
```

### Connection Issues

1. Check USB connection and power
2. Verify firmware loaded successfully
3. Check system logs for errors

## Development

### Project Structure

```
RTL8814AUDriver/
├── RTL8814AUDriver/          # DriverKit extension
│   ├── RTL8814AUDriver.swift # Main driver class
│   ├── USBInterface.swift    # USB communication
│   ├── NetworkInterface.swift # Network layer
│   └── Info.plist
├── RTL8814AUHelper/          # Helper application
│   └── HelperApp.swift
├── Firmware/                  # RTL8814AU firmware
├── Tests/                     # Unit and integration tests
└── Scripts/                   # Build and signing scripts
```

### Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Follow Swift style guidelines
4. Add tests for new features
5. Submit a pull request

## Legal & Licensing

- **Driver Code**: MIT License
- **Firmware**: Realtek proprietary (redistributable)
- **Apple Frameworks**: Used under Apple SDK license

### Disclaimer

This driver is provided "as is" without warranty. Use at your own risk.

## Credits

- Based on Realtek RTL8814AU specifications
- Inspired by Linux rtl8814au driver
- Built with Apple DriverKit framework

## Support

- **Issues**: [GitHub Issues](https://github.com/yourusername/rtl8814au-macos/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/rtl8814au-macos/discussions)
- **Documentation**: [Wiki](https://github.com/yourusername/rtl8814au-macos/wiki)

## Roadmap

- [x] Basic USB communication
- [x] Firmware loading
- [x] Network interface creation
- [ ] WPA2/WPA3 support
- [ ] Advanced power management
- [ ] Performance optimizations
- [ ] GUI configuration tool

---

Last updated: December 27, 2025
