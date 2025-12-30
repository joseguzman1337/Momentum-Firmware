# Quick Setup Guide

## 🚀 One-Line Installation

Choose one of these methods:

### Method 1: Interactive Launcher (Easiest)
```bash
chmod +x launcher.sh && ./launcher.sh
```

### Method 2: Automated Script
```bash
chmod +x install-rtl8814au.sh && ./install-rtl8814au.sh
```

### Method 3: Using Makefile
```bash
make install
```

### Method 4: Swift Builder
```bash
swift RTL8814AUDriverBuilder.swift
```

---

## 📁 Project Files

This project includes:

| File | Purpose |
|------|---------|
| `launcher.sh` | Interactive menu-driven installer |
| `install-rtl8814au.sh` | Automated bash installation script |
| `RTL8814AUDriverBuilder.swift` | Swift-based build automation |
| `rtl8814au-driver.rb` | Homebrew formula |
| `Makefile` | Build automation with make |
| `RTL8814AUDriverTests.swift` | Test suite |
| `README.md` | Complete documentation |
| `SETUP.md` | This quick guide |

---

## ⚡ Quick Commands

```bash
# Check if your system is ready
make check

# Install the driver
make install

# Verify it's working
make verify

# View logs
make logs

# Check USB devices
make usb-info

# Uninstall
make uninstall

# Run tests
swift test
```

---

## 🔄 Post-Installation Steps

1. **Restart your Mac**
   ```bash
   sudo reboot
   ```

2. **Approve the kernel extension**
   - Open **System Settings**
   - Go to **Privacy & Security**
   - Scroll down to **Security**
   - Click **Allow** next to "System software from developer..."
   - Restart again if prompted

3. **Verify installation**
   ```bash
   kextstat | grep rtl8814au
   ```

4. **Connect to WiFi**
   - Go to **System Settings > Network**
   - Your adapter should appear
   - Select a network and connect

---

## ⚠️ Important Notes

### System Integrity Protection (SIP)

**With SIP Enabled (Default - Recommended):**
- Driver requires approval in System Settings
- Multiple restarts may be needed
- Most secure option

**Check SIP Status:**
```bash
csrutil status
```

### Code Signing

For production use:
- Get Apple Developer Program membership ($99/year)
- Sign with Developer ID certificate
- Submit for notarization

Without signing:
- Driver will be unsigned
- More restrictive approval process
- May require SIP modifications

---

## 🐛 Troubleshooting

### Driver not loading?
```bash
# Check approval in System Settings
open "x-apple.systempreferences:com.apple.preference.security"

# Manually load
sudo kextload /Library/Extensions/rtl8814au.kext

# Check logs
log show --predicate 'process == "kernel"' --last 5m | grep rtl
```

### USB device not recognized?
```bash
# Check USB devices
system_profiler SPUSBDataType | grep -i realtek

# Try different port
# Use USB 3.0 if available
```

### Build errors?
```bash
# Update tools
xcode-select --install
brew update

# Clean rebuild
make clean
make build
```

---

## 🗑️ Uninstallation

```bash
# Method 1: Using make
make uninstall

# Method 2: Using launcher
./launcher.sh  # Choose option 2

# Method 3: Manual
sudo kextunload /Library/Extensions/rtl8814au.kext
sudo rm -rf /Library/Extensions/rtl8814au.kext
sudo kmutil install --update-all
sudo reboot
```

---

## 📚 More Information

See **README.md** for:
- Detailed documentation
- Complete troubleshooting guide
- Security considerations
- Code signing instructions
- Alternative solutions

---

## 🆘 Need Help?

1. Check README.md
2. Run the interactive launcher: `./launcher.sh`
3. Check logs: `make logs`
4. Open a GitHub issue

---

**Ready to install?**

```bash
./launcher.sh
```

or

```bash
make install
```

Good luck! 🎉
