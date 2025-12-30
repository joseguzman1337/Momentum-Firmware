# Quick Start Guide

Get your RTL8814AU WiFi adapter working on macOS Sequoia in minutes!

## Prerequisites

- **macOS Sequoia (15.0+)** - Required
- **System Integrity Protection (SIP) enabled** - Required  
- **Apple Developer Account** - Required for installation
- **Xcode 16.0+** - Required for building from source

## Installation Methods

### Method 1: Homebrew (Recommended for End Users)

```bash
# Add the tap
brew tap yourusername/rtl8814au

# Install the driver
brew install --cask rtl8814au-driver

# Follow the on-screen instructions to approve in System Settings
```

### Method 2: Build from Source (Recommended for Developers)

```bash
# Clone the repository
git clone https://github.com/yourusername/rtl8814au-macos.git
cd rtl8814au-macos

# Run setup script
chmod +x setup.sh
./setup.sh

# Build and install
make install
```

## After Installation

### 1. Approve System Extension

After installation, you'll see a system notification:

1. Click on the notification (or open it from Notification Center)
2. Click **"Allow"** in the notification
3. Alternatively, go to **System Settings → Privacy & Security**
4. Scroll down to the **Security** section
5. Find the entry for **RTL8814AU Driver**
6. Click **"Allow"**

### 2. Restart Your Mac

```bash
sudo reboot
```

### 3. Connect Your Device

After restart, connect your RTL8814AU USB WiFi adapter.

### 4. Verify Installation

```bash
# Check if the driver is loaded
systemextensionsctl list | grep RTL8814AU

# Check if device is recognized
system_profiler SPUSBDataType | grep -A 10 "RTL8814AU"

# Check network interfaces
ifconfig | grep en
```

## Troubleshooting

### Driver Not Loading

**Check SIP Status:**
```bash
csrutil status
```
Should say: "System Integrity Protection status: enabled"

**Check System Extensions:**
```bash
systemextensionsctl list
```
Look for `com.opensource.RTL8814AUDriver`

**View Logs:**
```bash
log stream --predicate 'subsystem == "com.opensource.RTL8814AUDriver"' --level debug
```

### Device Not Recognized

**Check USB Connection:**
```bash
system_profiler SPUSBDataType
```

**Verify Product ID:**
Supported devices:
- Vendor ID: `0x0bda` (Realtek)
- Product IDs: `0x8813`, `0x8834`

**Reset USB:**
```bash
sudo killall -STOP -c usbd
sleep 2
sudo killall -CONT -c usbd
```

### Permission Issues

```bash
# Reset system extension approvals
sudo systemextensionsctl reset

# Reinstall
sudo make install
```

## Uninstallation

### Via Homebrew

```bash
brew uninstall --cask rtl8814au-driver
```

### Manual Uninstall

```bash
# Using Makefile
sudo make uninstall

# Or manually
sudo systemextensionsctl uninstall com.opensource.RTL8814AUDriver com.opensource.RTL8814AUDriver
sudo rm -rf /Library/SystemExtensions/*/com.opensource.RTL8814AUDriver.dext
sudo reboot
```

## Configuration

### View Driver Status

```bash
make status
```

### Monitor Logs in Real-Time

```bash
make logs
```

### Check Network Interface

```bash
# List all network interfaces
networksetup -listallhardwareports

# Check specific interface (e.g., en7)
ifconfig en7

# View WiFi networks
networksetup -listpreferredwirelessnetworks en7
```

## Advanced Usage

### Developer Mode

For development and testing:

```bash
# Enable developer mode (skip notarization)
sudo systemextensionsctl developer on

# Build and install
make build
sudo make install

# When done
sudo systemextensionsctl developer off
```

### Custom Build

```bash
# Clean build
make clean

# Build with custom configuration
xcodebuild -project RTL8814AUDriver.xcodeproj \
           -scheme RTL8814AUDriver \
           -configuration Debug

# Install custom build
sudo cp -R build/RTL8814AUDriver.dext /Library/SystemExtensions/
```

### Firmware Management

Custom firmware can be placed in:
```
RTL8814AUDriver/Firmware/rtl8814au_fw.bin
```

Then rebuild:
```bash
make clean build install
```

## Performance Tips

### Check Signal Strength

```bash
sudo wdutil info
```

### Optimize for Speed

```bash
# Disable power management (temporary)
sudo pmset -a disksleep 0

# Reset network settings
sudo networksetup -setairportpower en7 off
sudo networksetup -setairportpower en7 on
```

## Command Reference

| Command | Description |
|---------|-------------|
| `make help` | Show all available commands |
| `make build` | Build the driver |
| `make install` | Install the driver (requires sudo) |
| `make uninstall` | Uninstall the driver (requires sudo) |
| `make status` | Check driver and device status |
| `make logs` | Stream driver logs |
| `make clean` | Clean build artifacts |
| `make verify` | Verify driver signature |

## System Requirements

| Component | Requirement |
|-----------|-------------|
| **macOS** | Sequoia (15.0+) |
| **SIP** | Enabled (required) |
| **RAM** | 4GB minimum |
| **USB** | 2.0 or 3.0 port |
| **Xcode** | 16.0+ (for building) |

## Supported Hardware

- **Realtek RTL8814AU** chipset
- Various USB WiFi adapters using this chipset
- USB 2.0 and USB 3.0 compatible

### Common Adapter Models

- ALFA Network AWUS1900
- ASUS USB-AC68
- Edimax EW-7833UAC
- Linksys WUSB6400M
- TP-Link Archer T9UH
- And others with RTL8814AU chipset

To verify your adapter's chipset:
```bash
system_profiler SPUSBDataType | grep -A 10 "Realtek"
```

## Getting Help

### Documentation

- **README.md** - Project overview and features
- **BUILDING.md** - Detailed build instructions
- **CONTRIBUTING.md** - How to contribute
- **CHANGELOG.md** - Version history

### Online Resources

- **GitHub Issues**: Report bugs or request features
  https://github.com/yourusername/rtl8814au-macos/issues

- **GitHub Discussions**: Ask questions and share tips
  https://github.com/yourusername/rtl8814au-macos/discussions

- **Wiki**: Comprehensive documentation
  https://github.com/yourusername/rtl8814au-macos/wiki

### Common Questions

**Q: Why do I need an Apple Developer account?**  
A: Code signing is required for system extensions on macOS.

**Q: Can I use this with SIP disabled?**  
A: The driver is designed for SIP enabled. Using with SIP disabled is not recommended or tested.

**Q: Will this work with macOS Sonoma?**  
A: This driver is specifically designed for macOS Sequoia (15.0+) using DriverKit.

**Q: How do I update the driver?**  
A: With Homebrew: `brew upgrade --cask rtl8814au-driver`  
   From source: `git pull && make install`

**Q: Does this support 5GHz WiFi?**  
A: Basic support is included. Advanced features are in development.

## Next Steps

Once your driver is installed and working:

1. **Configure WiFi**: Use System Settings → Wi-Fi to connect
2. **Test Performance**: Run speed tests
3. **Report Issues**: Help improve the driver by reporting bugs
4. **Contribute**: Consider contributing to the project

## Success Indicators

You'll know everything is working when you see:

✅ System extension appears in `systemextensionsctl list`  
✅ USB device recognized in `system_profiler SPUSBDataType`  
✅ Network interface appears in `ifconfig`  
✅ WiFi networks visible in System Settings  
✅ Internet connectivity through the adapter  

---

**Welcome to the RTL8814AU driver community!** 🎉

If you found this helpful, please star the project on GitHub!
