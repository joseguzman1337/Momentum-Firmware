# Changelog

All notable changes to the RTL8814AU macOS Driver will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Planned
- WPA2/WPA3 authentication support
- Advanced power management
- Performance optimizations
- GUI configuration utility
- 802.11ac/ax mode support
- Multi-band support (2.4GHz + 5GHz)

## [1.0.0] - 2025-12-27

### Added
- Initial release of RTL8814AU DriverKit driver
- macOS Sequoia (15.0+) support
- System Integrity Protection (SIP) compatibility
- USB device detection and initialization
- Firmware loading from bundle
- Network interface creation
- Basic USB communication layer
- Proper code signing and entitlements
- System extension integration
- Homebrew installation support
- Comprehensive documentation
  - README with quick start guide
  - BUILDING guide for developers
  - CONTRIBUTING guidelines
  - API documentation
- Build automation scripts
  - `build.sh` - Build driver
  - `sign.sh` - Code signing
  - `install.sh` - Installation
  - `Makefile` - Development workflow
- Test infrastructure with Swift Testing
- Logging with os_log
- Error handling and recovery
- Clean uninstallation support

### Features
- **DriverKit Implementation**: Modern, SIP-compatible driver architecture
- **USB Support**: Full USB 2.0/3.0 support for RTL8814AU
- **Network Interface**: Virtual network interface for WiFi connectivity
- **Firmware Management**: Automatic firmware loading and validation
- **Developer Experience**: Easy build, sign, and install workflow
- **Distribution**: Homebrew formula for easy installation

### Supported Hardware
- Realtek RTL8814AU (VID:0x0bda, PID:0x8813)
- Alternative RTL8814AU variants (PID:0x8834)

### Security
- Proper code signing with Developer ID
- Entitlements for DriverKit, USB, and networking
- App sandbox compliance
- Notarization support for distribution
- Works with SIP enabled (required)

### Documentation
- Complete API documentation
- User installation guide
- Developer building guide
- Contributing guidelines
- Troubleshooting wiki

### Known Limitations
- Basic connectivity only (no advanced features yet)
- WPA/WPA2/WPA3 authentication not yet implemented
- Manual network configuration required
- Limited power management
- No GUI configuration tool
- Single-band operation only

### System Requirements
- macOS Sequoia (15.0) or later
- System Integrity Protection enabled
- USB 2.0 or USB 3.0 port
- Apple Developer account (for building/signing)
- Xcode 16.0+ (for building from source)

### Technical Details
- Language: Swift 5.9+
- Frameworks: DriverKit, USBDriverKit, NetworkingDriverKit
- Architecture: arm64, x86_64
- Minimum Deployment Target: macOS 15.0

---

## Release Notes

### Version 1.0.0 (Initial Release)

This is the first public release of the RTL8814AU driver for macOS. It provides
basic functionality for USB WiFi adapters using the Realtek RTL8814AU chipset.

**What Works:**
- Driver loads and attaches to RTL8814AU devices
- Firmware uploads to device
- Network interface appears in system
- Basic USB communication
- Proper system integration with SIP enabled

**What's Coming:**
- Full WiFi protocol support
- WPA2/WPA3 encryption
- Improved performance
- GUI configuration
- Extended hardware support

**Installation:**

Via Homebrew:
```bash
brew tap yourusername/rtl8814au
brew install --cask rtl8814au-driver
```

From source:
```bash
git clone https://github.com/yourusername/rtl8814au-macos.git
cd rtl8814au-macos
make install
```

**Upgrading:**

For Homebrew users:
```bash
brew upgrade --cask rtl8814au-driver
```

Manual installations:
```bash
make uninstall
git pull
make install
```

**Important Notes:**

1. This driver requires SIP to be enabled
2. You must approve the system extension in System Settings
3. A restart is required after installation
4. Some features are still in development

**Feedback:**

Please report issues on GitHub:
https://github.com/yourusername/rtl8814au-macos/issues

---

## Development History

### Pre-release Development (2025-12)
- Initial DriverKit architecture design
- USB communication layer implementation
- Firmware loading mechanism
- Network interface abstraction
- Build and signing automation
- Documentation creation
- Open-source release preparation

---

## Migration Guide

### For Users of Older Kernel Extensions

If you previously used a kernel extension (kext) based driver for RTL8814AU,
you must uninstall it before using this DriverKit driver.

1. **Uninstall old kext:**
   ```bash
   sudo kextunload /Library/Extensions/RTL8814AU.kext
   sudo rm -rf /Library/Extensions/RTL8814AU.kext
   sudo kextcache -clear-staging
   ```

2. **Re-enable SIP** (if disabled):
   ```bash
   # Restart in Recovery Mode (Cmd+R on boot)
   # Open Terminal from Utilities menu
   csrutil enable
   # Restart normally
   ```

3. **Install new driver:**
   ```bash
   brew install --cask rtl8814au-driver
   ```

### Key Differences

- **No SIP disabling required**: Works with SIP enabled
- **System extension**: Uses DriverKit instead of kernel extension
- **User approval**: Requires explicit approval in System Settings
- **Automatic loading**: Loads automatically when device is connected
- **Modern architecture**: Built with Swift and modern APIs

---

## Support

- **Documentation**: [GitHub Wiki](https://github.com/yourusername/rtl8814au-macos/wiki)
- **Issues**: [GitHub Issues](https://github.com/yourusername/rtl8814au-macos/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/rtl8814au-macos/discussions)

[Unreleased]: https://github.com/yourusername/rtl8814au-macos/compare/v1.0.0...HEAD
[1.0.0]: https://github.com/yourusername/rtl8814au-macos/releases/tag/v1.0.0
