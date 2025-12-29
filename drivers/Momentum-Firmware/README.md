# RTL8814AU Driver for macOS Sequoia

**Open-source driver for Realtek RTL8814AU USB WiFi adapters on macOS Sequoia (15.0+) with SIP enabled**

## ⚠️ Important Disclaimer

This is an **open-source, community-maintained** driver that is:
- ❌ NOT officially supported by Apple
- ❌ NOT officially supported by Realtek  
- ❌ NOT signed or notarized by Apple (by default)
- ⚠️ Requires System Integrity Protection (SIP) considerations
- ⚠️ Use at your own risk

## 🎯 What This Project Does

This project provides **automated build and installation tools** for the RTL8814AU WiFi driver on macOS Sequoia. It includes:

1. **Automated installation script** (`install-rtl8814au.sh`)
2. **Swift-based build tool** (`RTL8814AUDriverBuilder.swift`)
3. **Homebrew formula** (`rtl8814au-driver.rb`)
4. Complete documentation and troubleshooting guides

## 📋 Prerequisites

### System Requirements
- **macOS Sequoia 15.0 or later**
- **RTL8814AU-based USB WiFi adapter**
- **Intel (x86_64) or Apple Silicon (ARM64) Mac**
- **At least 2GB free disk space**
- **Administrator access (sudo privileges)**

### Software Requirements
- **Xcode Command Line Tools**
- **Homebrew** (will be installed automatically if missing)
- Optional: **Apple Developer Account** (for code signing)

### Supported Devices

The RTL8814AU chipset is found in various USB WiFi adapters, including:
- ALFA AWUS1900
- Edimax EW-7833UAC
- ASUS USB-AC68
- TP-Link Archer T9UH
- Numerous generic adapters labeled "AC1900" or "1900Mbps"

Check your adapter's chipset with:
```bash
system_profiler SPUSBDataType | grep -A 10 Realtek
```

## 🚀 Quick Start Installation

### Method 1: Automated Bash Script (Recommended)

1. **Download the installation script:**
   ```bash
   curl -O https://raw.githubusercontent.com/YOUR_REPO/install-rtl8814au.sh
   chmod +x install-rtl8814au.sh
   ```

2. **Run the installer:**
   ```bash
   ./install-rtl8814au.sh
   ```

3. **Follow the on-screen instructions** and restart your Mac when prompted.

4. **Approve the kernel extension:**
   - Go to **System Settings > Privacy & Security**
   - Click **Allow** for the rtl8814au kernel extension
   - Restart again if required

### Method 2: Swift Build Tool

1. **Run the Swift builder:**
   ```bash
   swift RTL8814AUDriverBuilder.swift
   ```

2. **Follow the installation steps** provided by the tool.

### Method 3: Homebrew Formula

1. **Add the tap** (if you host this as a tap):
   ```bash
   brew tap YOUR_USERNAME/rtl8814au
   ```

2. **Install the driver:**
   ```bash
   brew install rtl8814au-driver
   ```

3. **Run the installer:**
   ```bash
   sudo rtl8814au-install
   ```

## 🔒 System Integrity Protection (SIP) Considerations

### Understanding SIP on macOS Sequoia

**System Integrity Protection (SIP)** is a security feature that restricts what can modify system files, including kernel extensions.

#### With SIP Enabled (Default & Recommended)

✅ **This is the secure, recommended approach**

To install kernel extensions with SIP enabled:
1. Driver must be **code-signed** with a Developer ID certificate
2. Driver must be **notarized** by Apple
3. User must **explicitly approve** the extension in System Settings

**For this driver:**
- Without a Developer ID certificate, it will be **unsigned**
- You'll need to approve it in **System Settings > Privacy & Security**
- macOS may require multiple restarts

#### With SIP Disabled (Not Recommended)

⚠️ **Only use this approach if absolutely necessary**

To temporarily disable SIP:

1. **Restart in Recovery Mode:**
   - **Intel Macs:** Hold `Cmd + R` during boot
   - **Apple Silicon Macs:** Hold the power button, select Options

2. **Open Terminal** from the Utilities menu

3. **Disable SIP:**
   ```bash
   csrutil disable
   ```

4. **Restart normally** and install the driver

5. **Re-enable SIP (IMPORTANT):**
   - Boot into Recovery Mode again
   - Run: `csrutil enable`
   - Restart

### Checking SIP Status

```bash
csrutil status
```

## 🔐 Code Signing (For Developers)

### Why Code Signing Matters

On macOS Sequoia with SIP enabled, unsigned kernel extensions are heavily restricted. Code signing with an Apple Developer ID:

- ✅ Allows installation without disabling SIP
- ✅ Provides cryptographic verification
- ✅ Enables notarization by Apple
- ✅ Gives users confidence in the driver's authenticity

### Requirements for Signing

1. **Apple Developer Program membership** ($99/year)
2. **Developer ID Application certificate**
3. **Xcode or command-line tools**

### Signing the Driver

```bash
# Find your signing identity
security find-identity -v -p codesigning

# Sign the kernel extension
codesign --force --deep --sign "Developer ID Application: YOUR NAME (TEAM_ID)" \
         --entitlements driver.entitlements \
         rtl8814au.kext

# Verify the signature
codesign --verify --verbose rtl8814au.kext
```

### Notarization

After signing, submit the driver to Apple for notarization:

```bash
# Create a ZIP of the signed kext
ditto -c -k --keepParent rtl8814au.kext rtl8814au.zip

# Submit for notarization
xcrun notarytool submit rtl8814au.zip \
     --apple-id YOUR_APPLE_ID \
     --team-id YOUR_TEAM_ID \
     --password YOUR_APP_SPECIFIC_PASSWORD \
     --wait

# Staple the notarization ticket
xcrun stapler staple rtl8814au.kext
```

## 🔧 Manual Installation Steps

If the automated scripts don't work, here's how to install manually:

### 1. Install Dependencies

```bash
# Install Homebrew (if not already installed)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install build dependencies
brew install git cmake pkg-config openssl@3

# Verify Xcode Command Line Tools
xcode-select --install
```

### 2. Clone and Build

```bash
# Clone the driver source
git clone https://github.com/morrownr/8814au.git
cd 8814au

# Build the driver
make clean
make -j$(sysctl -n hw.ncpu)
```

### 3. Install the Kernel Extension

```bash
# Copy to system extensions directory
sudo cp -R rtl8814au.kext /Library/Extensions/

# Set proper permissions
sudo chown -R root:wheel /Library/Extensions/rtl8814au.kext
sudo chmod -R 755 /Library/Extensions/rtl8814au.kext

# Update kernel extension cache
sudo kmutil install --update-all
```

### 4. Restart and Approve

1. **Restart your Mac**
2. Go to **System Settings > Privacy & Security**
3. **Allow** the rtl8814au kernel extension
4. **Restart again** if prompted

## ✅ Verification

### Check if Driver is Loaded

```bash
# List loaded kernel extensions
kextstat | grep rtl8814au

# Expected output:
# xxx  0  0xffffff7f8xxxx  0xxxxx  0xxxxx  com.realtek.rtl8814au (x.x.x)
```

### Verify USB Device

```bash
# Check if the adapter is recognized
system_profiler SPUSBDataType | grep -A 10 Realtek

# Check network interfaces
ifconfig -a | grep -A 5 "en"
```

### Test Network Connection

```bash
# List available WiFi networks
/System/Library/PrivateFrameworks/Apple80211.framework/Versions/Current/Resources/airport -s

# Check connection status
ifconfig en0  # or en1, en2, etc.
```

## 🐛 Troubleshooting

### Driver Not Loading After Restart

**Symptoms:**
- `kextstat | grep rtl8814au` shows nothing
- Adapter not visible in Network settings

**Solutions:**

1. **Check System Settings approval:**
   ```
   System Settings > Privacy & Security > Security
   ```
   Look for a message about blocked software and click Allow.

2. **Check kernel messages:**
   ```bash
   log show --predicate 'process == "kernel"' --last 10m | grep -i rtl
   ```

3. **Manually load the extension:**
   ```bash
   sudo kextload /Library/Extensions/rtl8814au.kext
   ```

4. **Check permissions:**
   ```bash
   ls -la /Library/Extensions/rtl8814au.kext
   # Should show: drwxr-xr-x  root  wheel
   ```

### Build Errors

**Error: `make: command not found`**
```bash
xcode-select --install
```

**Error: `git: command not found`**
```bash
brew install git
```

**Error: Architecture mismatch**
```bash
# Clean and rebuild
make clean
make ARCH=$(uname -m)
```

### USB Device Not Recognized

**Check if device is detected:**
```bash
system_profiler SPUSBDataType
```

**Try different USB port:**
- Use USB 3.0 port (blue port)
- Try direct connection (not through hub)
- Use different cable

**Reset USB controllers:**
```bash
sudo kextunload -b com.apple.driver.usb.AppleUSBXHCI
sudo kextload -b com.apple.driver.usb.AppleUSBXHCI
```

### WiFi Networks Not Showing

**Restart network services:**
```bash
sudo ifconfig en0 down
sudo ifconfig en0 up
```

**Reset WiFi preferences:**
```bash
sudo rm -rf /Library/Preferences/SystemConfiguration/com.apple.airport.preferences.plist
```

### Kernel Panics or System Instability

**Immediate action:**
1. Boot into **Safe Mode** (hold Shift during boot)
2. Uninstall the driver:
   ```bash
   sudo rm -rf /Library/Extensions/rtl8814au.kext
   sudo kmutil install --update-all
   ```
3. Restart normally

**Prevention:**
- Ensure you're using the latest driver version
- Check compatibility with your specific adapter model
- Consider using a native macOS-compatible adapter instead

## 🗑️ Uninstallation

### Method 1: Using Uninstall Script

If you used the automated installer:
```bash
sudo ~/uninstall-rtl8814au.sh
```

### Method 2: Using Homebrew

If installed via Homebrew:
```bash
sudo rtl8814au-uninstall
brew uninstall rtl8814au-driver
```

### Method 3: Manual Removal

```bash
# Unload the kernel extension
sudo kextunload /Library/Extensions/rtl8814au.kext

# Remove the driver
sudo rm -rf /Library/Extensions/rtl8814au.kext

# Update kernel cache
sudo kmutil install --update-all

# Restart your Mac
sudo reboot
```

## 📚 Additional Resources

### Driver Source Code
- **Primary repository:** https://github.com/morrownr/8814au
- **Alternative:** https://github.com/aircrack-ng/rtl8814au

### Documentation
- [Realtek RTL8814AU Datasheet](https://www.realtek.com/en/products/communications-network-ics/item/rtl8814au)
- [macOS Kernel Extensions Guide](https://developer.apple.com/library/archive/documentation/Darwin/Conceptual/KernelProgramming/)
- [System Integrity Protection](https://developer.apple.com/documentation/security/disabling_and_enabling_system_integrity_protection)

### Community Support
- GitHub Issues (this repository)
- [MacRumors Forums](https://forums.macrumors.com/)
- [r/MacOS on Reddit](https://www.reddit.com/r/MacOS/)

## 🤝 Contributing

Contributions are welcome! Please:

1. **Fork the repository**
2. **Create a feature branch:** `git checkout -b feature/improvement`
3. **Test thoroughly on macOS Sequoia**
4. **Submit a pull request** with detailed description

### Areas for Contribution
- [ ] Improved SIP compatibility
- [ ] DriverKit port (modern alternative to kernel extensions)
- [ ] Additional device support
- [ ] Bug fixes and stability improvements
- [ ] Documentation improvements

## 📄 License

This project is based on the open-source RTL8814AU driver which is licensed under **GPL-2.0**.

**License:** GNU General Public License v2.0

See [LICENSE](LICENSE) file for details.

## ⚠️ Legal & Safety Notices

### Disclaimer

This software is provided "as is", without warranty of any kind. The authors and contributors are not responsible for:
- Hardware damage
- Data loss
- System instability
- Security vulnerabilities
- Violation of laws or regulations

### Security Considerations

Installing third-party kernel extensions:
- ⚠️ Grants extensive system access
- ⚠️ Can compromise system security
- ⚠️ May violate corporate IT policies
- ⚠️ Could void warranty or support agreements

### Regulatory Compliance

- 📡 WiFi adapters must comply with local regulations (FCC, CE, etc.)
- 🌍 Some frequencies may be restricted in your region
- ⚖️ User is responsible for legal compliance

### Alternatives to Consider

Before installing this driver, consider:

1. **Native macOS-compatible adapters:**
   - No driver installation required
   - Full macOS integration
   - Better stability and security

2. **USB-Ethernet adapters:**
   - Wired connection may be more reliable
   - No driver issues

3. **Upgrade your Mac's built-in WiFi:**
   - Check if WiFi module is user-replaceable
   - Install Apple-compatible WiFi card

## 🎓 How This Works

### Architecture Overview

```
┌─────────────────────────────────────────────────┐
│         macOS Sequoia (User Space)              │
│                                                  │
│  ┌────────────────┐      ┌──────────────────┐  │
│  │ Network Prefs  │◄────►│  WiFi Menubar    │  │
│  └────────┬───────┘      └──────────────────┘  │
│           │                                      │
│           │ IOKit API                            │
├───────────┼──────────────────────────────────────┤
│  Kernel Space (Ring 0)                          │
│           │                                      │
│  ┌────────▼───────────┐                         │
│  │  rtl8814au.kext    │  ◄── Our Driver        │
│  │  (Kernel Extension)│                         │
│  └────────┬───────────┘                         │
│           │                                      │
│           │ USB API                              │
│  ┌────────▼───────────┐                         │
│  │  USB Stack         │                         │
│  └────────┬───────────┘                         │
└───────────┼──────────────────────────────────────┘
            │
            │ USB Protocol
┌───────────▼──────────────┐
│  RTL8814AU USB Adapter   │  ◄── Hardware
│  (Realtek Chipset)       │
└──────────────────────────┘
```

### Build Process

1. **Source Code:** C code for the RTL8814AU chipset
2. **Compilation:** Uses macOS kernel APIs
3. **Linking:** Creates `.kext` (kernel extension) bundle
4. **Signing:** Optional code signature with Developer ID
5. **Installation:** Copies to `/Library/Extensions/`
6. **Loading:** macOS kernel loads the extension
7. **Approval:** User approves in System Settings (SIP enabled)

## 📧 Support

For help with this project:

1. **Check the Troubleshooting section** above
2. **Search existing GitHub Issues**
3. **Open a new issue** with:
   - macOS version (`sw_vers`)
   - SIP status (`csrutil status`)
   - USB device info (`system_profiler SPUSBDataType`)
   - Relevant logs
   - Steps to reproduce

---

**Last Updated:** December 27, 2025
**Compatible with:** macOS Sequoia 15.0+
**Project Status:** Active Development

**Happy WiFi-ing! 📶**
