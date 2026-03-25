# Complete Development & Deployment Guide

This guide provides step-by-step instructions for the complete lifecycle of the RTL8814AU driver, from development to distribution.

## 📋 Table of Contents

1. [Initial Setup](#initial-setup)
2. [Development Environment](#development-environment)
3. [Code Signing Setup](#code-signing-setup)
4. [Building the Driver](#building-the-driver)
5. [Testing](#testing)
6. [Code Signing & Notarization](#code-signing--notarization)
7. [Local Installation](#local-installation)
8. [Distribution](#distribution)
9. [Homebrew Publishing](#homebrew-publishing)
10. [CI/CD Setup](#cicd-setup)
11. [Maintenance](#maintenance)

---

## Initial Setup

### 1. System Requirements Check

```bash
# Check macOS version (must be Sequoia 15.0+)
sw_vers -productVersion

# Check SIP status (must be enabled for production)
csrutil status

# Check Xcode (must be 16.0+)
xcodebuild -version

# Check Swift
swift --version
```

### 2. Clone Repository

```bash
git clone https://github.com/yourusername/rtl8814au-macos.git
cd rtl8814au-macos
```

### 3. Run Setup Script

```bash
chmod +x setup.sh
./setup.sh
```

This script will:
- Verify system requirements
- Check for required tools
- Install optional development tools
- Setup code signing
- Prepare build environment

---

## Development Environment

### Required Tools

```bash
# Install Xcode from App Store or developer.apple.com

# Install Homebrew
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install development tools
brew install swiftlint
brew install swift-format
brew install gh  # GitHub CLI (optional)
```

### Configure Git

```bash
git config user.name "Your Name"
git config user.email "your@email.com"

# Setup upstream
git remote add upstream https://github.com/yourusername/rtl8814au-macos.git
```

### IDE Setup

**Xcode:**
```bash
# Open project
open RTL8814AUDriver.xcodeproj
```

**VS Code (optional):**
```bash
# Install extensions
code --install-extension vknabel.vscode-swift-development-environment
code --install-extension sswg.swift-lang
```

---

## Code Signing Setup

### 1. Apple Developer Account

1. Sign up at https://developer.apple.com
2. Join the Apple Developer Program ($99/year for distribution)

### 2. Create Signing Certificate

1. Go to https://developer.apple.com/account
2. Navigate to "Certificates, Identifiers & Profiles"
3. Click "+" to create new certificate
4. Select "Developer ID Application"
5. Follow steps to create CSR (Certificate Signing Request):
   ```bash
   # In Keychain Access: 
   # Certificate Assistant → Request Certificate from Certificate Authority
   # Save to disk
   ```
6. Upload CSR and download certificate
7. Double-click .cer file to install in Keychain

### 3. Configure Signing Identity

```bash
# Find your signing identity
security find-identity -v -p codesigning

# Set environment variables
export CODESIGN_IDENTITY="Developer ID Application: Your Name (TEAM_ID)"
export TEAM_ID="YOUR_TEAM_ID"

# Add to ~/.zshrc or ~/.bash_profile for persistence
echo 'export TEAM_ID="YOUR_TEAM_ID"' >> ~/.zshrc
echo 'export CODESIGN_IDENTITY="Developer ID Application: Your Name (TEAM_ID)"' >> ~/.zshrc
```

### 4. Update Project Files

Edit these files with your Team ID:
- `Makefile` (line with TEAM_ID)
- `build.sh` (line with TEAM_ID)
- `sign.sh` (line with TEAM_ID)
- `RTL8814AUDriver.xcodeproj/project.pbxproj` (DEVELOPMENT_TEAM)

---

## Building the Driver

### Using Makefile (Recommended)

```bash
# Build debug version
make build

# Build release version
xcodebuild -project RTL8814AUDriver.xcodeproj \
           -scheme RTL8814AUDriver \
           -configuration Release \
           clean build
```

### Using Xcode

1. Open `RTL8814AUDriver.xcodeproj`
2. Select scheme: RTL8814AUDriver
3. Choose configuration: Debug or Release
4. Product → Build (Cmd+B)

### Build Output

The built driver will be at:
```
DerivedData/Build/Products/Release/RTL8814AUDriver.dext
```

Or when using build.sh:
```
build/RTL8814AUDriver.dext
```

### Verify Build

```bash
# Check if .dext exists
ls -l build/RTL8814AUDriver.dext

# Check Info.plist
plutil -lint build/RTL8814AUDriver.dext/Contents/Info.plist

# Check executable
file build/RTL8814AUDriver.dext/Contents/MacOS/RTL8814AUDriver
```

---

## Testing

### Unit Tests

```bash
# Run all tests
swift test

# Run specific test
swift test --filter DriverInitializationTests

# Run with coverage
swift test --enable-code-coverage

# View coverage report
xcrun llvm-cov show .build/debug/RTL8814AUDriverPackageTests.xctest \
  -instr-profile .build/debug/codecov/default.profdata
```

### Integration Testing

```bash
# Enable developer mode (skip notarization requirement)
sudo systemextensionsctl developer on

# Build and install
make build
sudo make install

# Connect test device

# Monitor logs in real-time
make logs

# In another terminal, check status
make status

# Test functionality
# ... perform manual testing ...

# When done, disable developer mode
sudo systemextensionsctl developer off
```

### Manual Testing Checklist

- [ ] Driver loads on boot
- [ ] Device is recognized when connected
- [ ] Firmware uploads successfully
- [ ] Network interface appears
- [ ] Can scan for WiFi networks
- [ ] Can connect to network
- [ ] Data transfer works
- [ ] Driver unloads cleanly
- [ ] No kernel panics or crashes
- [ ] Logs show no errors

---

## Code Signing & Notarization

### 1. Sign the Driver

```bash
./sign.sh
```

Or manually:
```bash
codesign --sign "Developer ID Application: Your Name (TEAM_ID)" \
         --force \
         --options runtime \
         --timestamp \
         --deep \
         --entitlements RTL8814AUDriver/RTL8814AUDriver.entitlements \
         --identifier com.opensource.RTL8814AUDriver \
         build/RTL8814AUDriver.dext
```

### 2. Verify Signature

```bash
# Verify signature
codesign -vvv --deep --strict build/RTL8814AUDriver.dext

# Check signature details
codesign -dvv build/RTL8814AUDriver.dext

# Verify entitlements
codesign -d --entitlements :- build/RTL8814AUDriver.dext
```

### 3. Create App-Specific Password

For notarization:

1. Go to https://appleid.apple.com
2. Sign in with your Apple ID
3. In Security section, click "App-Specific Passwords"
4. Click "+" to generate new password
5. Save the password securely

### 4. Notarize the Driver

```bash
# Create ZIP for notarization
cd build
zip -r RTL8814AUDriver.zip RTL8814AUDriver.dext
cd ..

# Submit for notarization
xcrun notarytool submit build/RTL8814AUDriver.zip \
  --apple-id your@email.com \
  --team-id YOUR_TEAM_ID \
  --password YOUR_APP_SPECIFIC_PASSWORD \
  --wait

# Save credentials (optional)
xcrun notarytool store-credentials "RTL8814AU-Profile" \
  --apple-id your@email.com \
  --team-id YOUR_TEAM_ID \
  --password YOUR_APP_SPECIFIC_PASSWORD

# Use saved credentials
xcrun notarytool submit build/RTL8814AUDriver.zip \
  --keychain-profile "RTL8814AU-Profile" \
  --wait
```

### 5. Staple Notarization Ticket

```bash
# After successful notarization
xcrun stapler staple build/RTL8814AUDriver.dext

# Verify stapling
xcrun stapler validate build/RTL8814AUDriver.dext

# Check Gatekeeper assessment
spctl --assess --type install build/RTL8814AUDriver.dext
```

---

## Local Installation

### For Development

```bash
# Enable developer mode
sudo systemextensionsctl developer on

# Install
sudo make install

# Approve in System Settings when prompted
```

### For Production Testing

```bash
# Build, sign, and notarize first
./build.sh
./sign.sh
# ... notarize ...

# Disable developer mode
sudo systemextensionsctl developer off

# Install
sudo ./install.sh

# Restart
sudo reboot
```

### Verification

```bash
# Check system extension
systemextensionsctl list | grep RTL8814AU

# Check USB device
system_profiler SPUSBDataType | grep -A 10 "RTL8814AU"

# Check network interface
ifconfig | grep en

# View logs
log stream --predicate 'subsystem == "com.opensource.RTL8814AUDriver"'
```

---

## Distribution

### Create Release Package

```bash
# Build release version
make clean build sign

# Create distribution archive
make dist

# Output: build/RTL8814AUDriver-Release.tar.gz
```

### GitHub Release

```bash
# Tag version
git tag -a v1.0.0 -m "Release version 1.0.0"
git push origin v1.0.0

# Create release using GitHub CLI
gh release create v1.0.0 \
  build/RTL8814AUDriver-Release.tar.gz \
  --title "RTL8814AU Driver v1.0.0" \
  --notes "Release notes here"

# Or create manually at:
# https://github.com/yourusername/rtl8814au-macos/releases/new
```

### Calculate SHA256

```bash
# For Homebrew formula
shasum -a 256 build/RTL8814AUDriver-Release.tar.gz
```

---

## Homebrew Publishing

### 1. Create Tap Repository

```bash
# Create new repository on GitHub: homebrew-rtl8814au
mkdir homebrew-rtl8814au
cd homebrew-rtl8814au
git init

# Create Casks directory
mkdir Casks
cp ../rtl8814au-macos/Homebrew/rtl8814au-driver.rb Casks/

# Update SHA256 in formula
# Edit Casks/rtl8814au-driver.rb with actual SHA256

git add .
git commit -m "Initial formula"
git remote add origin https://github.com/yourusername/homebrew-rtl8814au.git
git push -u origin main
```

### 2. Update Formula

After each release:

```bash
cd homebrew-rtl8814au

# Update version and SHA256 in Casks/rtl8814au-driver.rb
# Get SHA256 from release asset

git add Casks/rtl8814au-driver.rb
git commit -m "Update to v1.0.0"
git push
```

### 3. Test Formula

```bash
# Test installation
brew install --cask rtl8814au-driver

# Test uninstallation
brew uninstall --cask rtl8814au-driver

# Audit formula
brew audit --cask --strict rtl8814au-driver
```

---

## CI/CD Setup

### GitHub Actions Configuration

The `.github/workflows/build.yml` is already configured to:
- Lint code on every push
- Build debug and release versions
- Run tests
- Perform security checks
- Create releases automatically

### Required Secrets

Add these to GitHub repository secrets:

```
Settings → Secrets and variables → Actions → New repository secret

APPLE_ID: your@email.com
APPLE_TEAM_ID: YOUR_TEAM_ID
APPLE_APP_PASSWORD: your-app-specific-password
CODESIGN_CERTIFICATE: base64-encoded .p12 file
CODESIGN_PASSWORD: password for .p12
```

### Export Signing Certificate

```bash
# Export from Keychain as .p12
# Keychain Access → Find certificate → Export

# Convert to base64 for GitHub secrets
base64 -i YourCertificate.p12 | pbcopy
# Paste into CODESIGN_CERTIFICATE secret
```

---

## Maintenance

### Updating Dependencies

```bash
# Update Xcode
# Download from App Store or developer.apple.com

# Update Homebrew tools
brew update
brew upgrade swiftlint swift-format

# Check for Swift updates
swift --version
```

### Monitoring Issues

```bash
# Check GitHub issues
gh issue list

# Check discussions
gh pr list

# View repository activity
gh repo view --web
```

### Version Bumping

```bash
# Update version in:
# - RTL8814AUDriver/Info.plist (CFBundleShortVersionString)
# - RTL8814AUDriver.xcodeproj/project.pbxproj (MARKETING_VERSION)
# - Homebrew/rtl8814au-driver.rb (version)
# - CHANGELOG.md (new entry)

# Commit changes
git add .
git commit -m "Bump version to 1.1.0"

# Tag and push
git tag v1.1.0
git push origin main --tags
```

### Responding to Bugs

1. **Reproduce**: Try to reproduce the issue
2. **Diagnose**: Collect logs and system info
3. **Fix**: Make necessary code changes
4. **Test**: Verify fix works
5. **Release**: Create patch release
6. **Document**: Update changelog

### Security Updates

```bash
# Check for security issues
grep -r "TODO.*security" RTL8814AUDriver/
grep -r "FIXME.*security" RTL8814AUDriver/

# Run security audit
make security

# Update dependencies regularly
```

---

## Checklists

### Pre-Release Checklist

- [ ] All tests pass
- [ ] Code is linted and formatted
- [ ] Documentation is updated
- [ ] CHANGELOG.md is updated
- [ ] Version numbers are bumped
- [ ] Driver is signed
- [ ] Driver is notarized
- [ ] Release notes are written
- [ ] Installation tested on clean system
- [ ] Homebrew formula is updated

### Post-Release Checklist

- [ ] GitHub release created
- [ ] Release assets uploaded
- [ ] Homebrew formula published
- [ ] Documentation site updated
- [ ] Announcement posted
- [ ] Issues/discussions monitored
- [ ] Feedback collected

---

## Useful Commands Reference

```bash
# Development
make help                    # Show all commands
make build                   # Build driver
make clean                   # Clean build
make test                    # Run tests
make lint                    # Lint code
make format                  # Format code

# Installation
sudo make install            # Install driver
sudo make uninstall          # Uninstall driver
make status                  # Check status
make logs                    # Stream logs

# Code signing
make sign                    # Sign driver
make verify                  # Verify signature

# Distribution
make dist                    # Create distribution package

# System extensions
sudo systemextensionsctl list                 # List extensions
sudo systemextensionsctl developer on/off     # Toggle dev mode
sudo systemextensionsctl reset                # Reset database

# Debugging
log show --predicate 'subsystem == "com.opensource.RTL8814AUDriver"' --last 1h
log stream --predicate 'subsystem == "com.opensource.RTL8814AUDriver"' --level debug
system_profiler SPUSBDataType
ifconfig -a
networksetup -listallhardwareports
```

---

## Resources

- [Apple DriverKit Documentation](https://developer.apple.com/documentation/driverkit)
- [System Extensions Programming Guide](https://developer.apple.com/documentation/systemextensions)
- [Code Signing Guide](https://developer.apple.com/documentation/security/notarizing_macos_software_before_distribution)
- [Homebrew Cask Documentation](https://docs.brew.sh/Cask-Cookbook)

---

## Getting Help

- **Issues**: https://github.com/yourusername/rtl8814au-macos/issues
- **Discussions**: https://github.com/yourusername/rtl8814au-macos/discussions
- **Wiki**: https://github.com/yourusername/rtl8814au-macos/wiki

---

Last updated: December 27, 2025
