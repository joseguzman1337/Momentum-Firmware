# Building and Installing RTL8814AU Driver

This guide walks through building, signing, and installing the RTL8814AU driver on macOS Sequoia.

## Prerequisites

### Required Tools

1. **Xcode 16.0 or later**
   ```bash
   xcode-select --install
   ```

2. **Homebrew** (for distribution)
   ```bash
   /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
   ```

3. **Apple Developer Account** (for signing)
   - Free account: For personal development only
   - Paid account: Required for distribution

### Code Signing Setup

1. **Install Developer ID Certificate**
   - Sign in to developer.apple.com
   - Go to Certificates, Identifiers & Profiles
   - Create a "Developer ID Application" certificate
   - Download and install in Keychain Access

2. **Set Environment Variables**
   ```bash
   export CODESIGN_IDENTITY="Developer ID Application: Your Name (TEAM_ID)"
   export TEAM_ID="YOUR_TEAM_ID"
   ```

## Building the Driver

### Step 1: Clone Repository

```bash
git clone https://github.com/yourusername/rtl8814au-macos.git
cd rtl8814au-macos
```

### Step 2: Build

```bash
chmod +x build.sh
./build.sh
```

The build script will:
- Clean previous builds
- Compile the DriverKit extension
- Verify the build
- Create distribution package

Expected output:
```
================================
Build completed successfully!
================================

Driver location: build/RTL8814AUDriver.dext
Distribution package: build/RTL8814AUDriver-Release.tar.gz
```

### Step 3: Sign the Driver

```bash
chmod +x sign.sh
./sign.sh
```

The signing script will:
- Apply Developer ID signature
- Add required entitlements
- Verify the signature
- Optionally prepare for notarization

### Step 4: Notarize (for distribution)

If you plan to distribute the driver, you must notarize it:

```bash
# Create app-specific password at appleid.apple.com
# Then notarize:

xcrun notarytool submit build/RTL8814AUDriver.zip \
  --apple-id your@email.com \
  --team-id YOUR_TEAM_ID \
  --password YOUR_APP_SPECIFIC_PASSWORD \
  --wait

# After success, staple the ticket:
xcrun stapler staple build/RTL8814AUDriver.dext
```

## Installing the Driver

### Method 1: Direct Installation

```bash
chmod +x install.sh
sudo ./install.sh
```

Follow the on-screen prompts to:
1. Approve the system extension notification
2. Open System Settings → Privacy & Security
3. Click "Allow" for the driver
4. Restart your Mac

### Method 2: Homebrew Installation

```bash
# Add the tap
brew tap yourusername/rtl8814au

# Install
brew install --cask rtl8814au-driver
```

## Verifying Installation

### Check System Extensions

```bash
systemextensionsctl list
```

Look for `com.opensource.RTL8814AUDriver` in the list.

### Monitor Driver Logs

```bash
log stream --predicate 'subsystem == "com.opensource.RTL8814AUDriver"' --level debug
```

### Check USB Device

```bash
system_profiler SPUSBDataType | grep -A 10 "RTL8814AU"
```

### Test Network Interface

After connecting the device:

```bash
ifconfig | grep en
networksetup -listallhardwareports
```

## Troubleshooting

### Driver Not Loading

1. **Check SIP Status**
   ```bash
   csrutil status
   ```
   Should show: "System Integrity Protection status: enabled"

2. **Verify Signature**
   ```bash
   codesign -vvv --deep --strict build/RTL8814AUDriver.dext
   ```

3. **Check Approval Status**
   - Open System Settings
   - Go to Privacy & Security
   - Scroll to Security section
   - Look for pending approval

### Device Not Recognized

1. **Check USB Connection**
   ```bash
   system_profiler SPUSBDataType
   ```

2. **Verify Product ID**
   The driver supports:
   - 0x0bda:0x8813 (RTL8814AU)
   - 0x0bda:0x8834 (Alternative)

3. **Reset USB**
   ```bash
   sudo killall -STOP -c usbd
   sleep 2
   sudo killall -CONT -c usbd
   ```

### Uninstall Driver

```bash
# Uninstall system extension
sudo systemextensionsctl uninstall com.opensource.RTL8814AUDriver com.opensource.RTL8814AUDriver

# Remove files
sudo rm -rf /Library/SystemExtensions/*/com.opensource.RTL8814AUDriver.dext

# Restart
sudo reboot
```

## Development Builds

For development and testing without full signing:

```bash
# Enable developer mode
sudo systemextensionsctl developer on

# Build and install
./build.sh
sudo ./install.sh

# When done developing
sudo systemextensionsctl developer off
```

## Advanced Configuration

### Custom Firmware

Place custom firmware in `RTL8814AUDriver/Firmware/`:

```bash
mkdir -p RTL8814AUDriver/Firmware
cp path/to/rtl8814au_fw.bin RTL8814AUDriver/Firmware/
./build.sh
```

### Modify Info.plist

Add support for additional product IDs:

```xml
<key>RTL8814AU_USB_Driver_Custom</key>
<dict>
    <key>idVendor</key>
    <integer>YOUR_VENDOR_ID</integer>
    <key>idProduct</key>
    <integer>YOUR_PRODUCT_ID</integer>
    ...
</dict>
```

### Debug Builds

```bash
# Build debug version
xcodebuild -project RTL8814AUDriver.xcodeproj \
           -scheme RTL8814AUDriver \
           -configuration Debug
```

## CI/CD Integration

### GitHub Actions

```yaml
name: Build Driver
on: [push, pull_request]

jobs:
  build:
    runs-on: macos-14
    steps:
      - uses: actions/checkout@v4
      - name: Build
        run: ./build.sh
      - name: Upload Artifact
        uses: actions/upload-artifact@v4
        with:
          name: RTL8814AUDriver
          path: build/RTL8814AUDriver.dext
```

## Support

- **Issues**: [GitHub Issues](https://github.com/yourusername/rtl8814au-macos/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/rtl8814au-macos/discussions)
- **Documentation**: [Wiki](https://github.com/yourusername/rtl8814au-macos/wiki)

## References

- [Apple DriverKit Documentation](https://developer.apple.com/documentation/driverkit)
- [System Extensions Guide](https://developer.apple.com/documentation/systemextensions)
- [Code Signing Guide](https://developer.apple.com/documentation/security/notarizing_macos_software_before_distribution)
