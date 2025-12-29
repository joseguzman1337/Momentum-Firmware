# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Planned
- WPA3 encryption support
- Advanced 802.11ac features (MU-MIMO, beamforming)
- Power management optimization
- Roaming support
- Background scanning
- Better error recovery

## [1.0.0] - 2024-12-27

### Added
- Initial release
- DriverKit-based userspace driver (no KEXT required)
- Full SIP compatibility
- RTL8814AU chipset support
- USB communication layer
- Basic WiFi functionality:
  - Network scanning
  - WPA2 connection
  - Data transmission and reception
- 802.11a/b/g/n/ac support
- Dual-band support (2.4 GHz and 5 GHz)
- 4x4 MIMO support
- Channel management
- Build automation scripts
- Installation and uninstallation scripts
- Unit tests
- Documentation

### Technical Details
- Swift 6.0
- DriverKit framework
- USB bulk and control transfers
- System extension architecture
- Code signing and notarization support

### Supported Hardware
- Realtek RTL8814AU chipset
- USB Vendor ID: 0x0bda
- USB Product IDs: 0x8813, 0x8814

### Supported Platforms
- macOS Sequoia (15.0) and later

### Known Limitations
- Firmware binary needs to be integrated (placeholder currently)
- WPA3 not yet supported
- Some advanced 802.11ac features not yet implemented
- Power management basic
- Limited testing on various hardware configurations

## Development Milestones

### Phase 1: Foundation ✅
- DriverKit project structure
- USB communication layer
- Basic hardware initialization
- System extension framework

### Phase 2: WiFi Basic Features ✅
- Channel management
- Network scanning
- Basic connection support
- Data transmission

### Phase 3: In Progress 🚧
- Firmware integration
- WPA2/WPA3 full implementation
- Performance optimization
- Comprehensive testing

### Phase 4: Planned 📋
- Advanced features (roaming, power management)
- Additional chipset support
- Production hardening
- App Store distribution
