# RTL88xxAU macOS Driver

A macOS kernel extension (kext) driver for Realtek RTL8812AU, RTL8821AU, and RTL8814AU USB WiFi adapters, including the popular Alfa AWUS1900.

## Supported Devices

### Realtek Chipsets
- **RTL8812AU** - Dual-band 802.11ac USB 3.0 WiFi adapter
- **RTL8821AU** - Single-band 802.11ac USB WiFi adapter  
- **RTL8814AU** - Dual-band 802.11ac USB 3.0 WiFi adapter with 4x4 MIMO

### Tested Hardware
- Alfa AWUS1900 (RTL8814AU)
- Alfa AWUS036ACS (RTL8812AU)
- Various generic RTL8812AU/RTL8821AU adapters

## System Requirements

- **macOS**: Version 26.3 Beta (25D5087f) macOS Tahoe or later
- **Architecture**: Intel x86_64 and Apple Silicon (ARM64) Apple M1, M2, M3, M4, M5, M6, M7 Pro + Max
- **Xcode**: Latest version with command line tools
- **System Integrity Protection**: May need to be disabled for installation

## Installation

### Option 1: Pre-built Package (Recommended)

1. Download the latest `.pkg` installer from the releases page
2. Double-click the package and follow the installation wizard
3. Restart your Mac
4. Connect your RTL88xxAU device

### Option 2: Build from Source

1. Clone this repository:
   ```bash
   git clone https://github.com/realtek/rtl88xxau-macos-driver.git
   cd rtl88xxau-macos-driver
   ```

2. Build the driver:
   ```bash
   make build
   ```

3. Install the driver (requires admin privileges):
   ```bash
   sudo make install
   ```

4. Load the driver:
   ```bash
   sudo make load
   ```

## Usage

### Loading/Unloading the Driver

```bash
# Load the driver
sudo kextload /System/Library/Extensions/RTL88xxAU.kext

# Unload the driver  
sudo kextunload /System/Library/Extensions/RTL88xxAU.kext

# Check if driver is loaded
kextstat | grep RTL88xxAU
```

### Viewing Driver Logs

```bash
# View system logs for the driver
log show --predicate 'senderImagePath contains "RTL88xxAU"' --info

# Monitor logs in real-time
log stream --predicate 'senderImagePath contains "RTL88xxAU"' --info
```

## Building

### Prerequisites

- Xcode with command line tools installed
- macOS SDK (automatically installed with Xcode)

### Build Commands

```bash
# Build the kernel extension
make build

# Create installer package
make package

# Clean build files
make clean

# Test the extension (without installing)
make test

# Show all available commands
make help
```

### Build Output

- `build/RTL88xxAU.kext` - The kernel extension
- `build/RTL88xxAU-1.0.0.pkg` - Installer package

## Troubleshooting

### Common Issues

1. **Driver not loading**
   - Check System Integrity Protection status: `csrutil status`
   - Ensure your device is supported: `system_profiler SPUSBDataType`
   - Check kernel logs: `dmesg | grep RTL88xxAU`

2. **Network interface not appearing**
   - Verify driver is loaded: `kextstat | grep RTL88xxAU`
   - Check for conflicting drivers: `kextstat | grep -i realtek`
   - Restart Network preferences or run: `sudo ifconfig en1 down && sudo ifconfig en1 up`

3. **Installation fails**
   - Disable System Integrity Protection temporarily
   - Clear kernel extension cache: `sudo kextcache -clear-cache`
   - Ensure no other RTL drivers are installed

### System Integrity Protection (SIP)

If you encounter installation issues, you may need to disable SIP:

1. Boot into Recovery Mode (hold Cmd+R during startup)
2. Open Terminal from Utilities menu
3. Run: `csrutil disable`
4. Restart and install the driver
5. Re-enable SIP: `csrutil enable`

### Debug Mode

Enable verbose logging by building with debug flags:

```bash
make clean
make build DEBUG=1
```

## Device Detection

Check if your device is detected:

```bash
# List USB devices
system_profiler SPUSBDataType | grep -A5 -B5 -i realtek

# Check for Realtek devices specifically
ioreg -p IOUSB -w0 | grep -i realtek
```

## Monitor Mode Support

This driver includes preliminary support for monitor mode on compatible hardware:

```bash
# Enable monitor mode (experimental)
sudo ifconfig wlan0 mediaopt monitor

# Capture packets
sudo tcpdump -i wlan0 -w capture.pcap
```

## Development

### Project Structure

```
RTL88xxAU-macOS-Driver/
├── src/
│   ├── RTL88xxAU.h          # Main driver header
│   ├── RTL88xxAU.cpp        # Main driver implementation
│   └── kext/
│       └── RTL88xxAU.kext/
│           └── Contents/
│               └── Info.plist # Kernel extension metadata
├── build/                    # Build output directory
├── docs/                     # Documentation
├── scripts/                  # Utility scripts  
├── Makefile                  # Build system
└── README.md                 # This file
```

### Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes and test thoroughly
4. Submit a pull request with detailed description

### Debugging

1. Enable kernel debugging in `boot-args`:
   ```bash
   sudo nvram boot-args="kext-dev-mode=1 debug=0x146"
   ```

2. Use `kextutil` for testing:
   ```bash
   sudo kextutil -t build/RTL88xxAU.kext
   ```

3. Monitor kernel logs:
   ```bash
   tail -f /var/log/kernel.log | grep RTL88xxAU
   ```

## License

This project is based on the Linux RTL8812AU driver and is licensed under the GNU General Public License v2.0.

## Disclaimer

This driver is provided as-is without warranty. Use at your own risk. The authors are not responsible for any damage to your system or hardware.

## Support

- **GitHub Issues**: Report bugs and request features
- **Wiki**: Additional documentation and guides
- **Discussions**: Community support and general questions

## Acknowledgments

- Original Linux driver developers at Realtek
- macOS kernel extension development community
- Beta testers and contributors

---

**Note**: This is an unofficial driver not endorsed by Realtek or Apple. Support is community-driven.
