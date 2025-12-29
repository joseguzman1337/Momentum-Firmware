# Troubleshooting Guide

Comprehensive solutions for common issues with the RTL8814AU driver.

## Table of Contents

- [Installation Issues](#installation-issues)
- [Driver Loading Problems](#driver-loading-problems)
- [Device Recognition Issues](#device-recognition-issues)
- [Connection Problems](#connection-problems)
- [Performance Issues](#performance-issues)
- [Build and Signing Issues](#build-and-signing-issues)
- [System Extension Issues](#system-extension-issues)
- [Diagnostic Commands](#diagnostic-commands)

---

## Installation Issues

### Error: "Driver signature is invalid"

**Symptoms:**
- Installation fails with signature verification error
- `codesign` verification fails

**Solutions:**

1. **Re-sign the driver:**
   ```bash
   ./sign.sh
   ```

2. **Check signing identity:**
   ```bash
   security find-identity -v -p codesigning
   ```

3. **Verify entitlements:**
   ```bash
   codesign -d --entitlements :- build/RTL8814AUDriver.dext
   ```

4. **Clean and rebuild:**
   ```bash
   make clean build sign
   ```

### Error: "Operation not permitted"

**Symptoms:**
- Installation fails with permission errors
- Cannot copy to `/Library/SystemExtensions`

**Solutions:**

1. **Use sudo:**
   ```bash
   sudo make install
   # or
   sudo ./install.sh
   ```

2. **Check System Settings:**
   - System Settings → Privacy & Security
   - Check for pending approvals

3. **Reset system extension database:**
   ```bash
   sudo systemextensionsctl reset
   ```

### Error: "SIP is disabled"

**Symptoms:**
- Warning about SIP being disabled
- Driver may not load properly

**Solutions:**

1. **Enable SIP:**
   - Restart in Recovery Mode (hold Cmd+R during boot)
   - Open Terminal from Utilities menu
   - Run: `csrutil enable`
   - Restart normally

2. **Verify SIP status:**
   ```bash
   csrutil status
   ```
   Should show: "System Integrity Protection status: enabled"

---

## Driver Loading Problems

### Driver Not Appearing in systemextensionsctl list

**Symptoms:**
- `systemextensionsctl list` doesn't show the driver
- No system extension notification

**Solutions:**

1. **Check installation path:**
   ```bash
   sudo find /Library/SystemExtensions -name "*RTL8814AU*"
   ```

2. **Force activation:**
   ```bash
   sudo systemextensionsctl developer on
   sudo systemextensionsctl list
   ```

3. **Check logs for errors:**
   ```bash
   log show --predicate 'subsystem == "com.apple.SystemExtensions"' \
            --last 10m \
            --info
   ```

4. **Reinstall:**
   ```bash
   sudo make uninstall
   sudo reboot
   # After reboot:
   sudo make install
   ```

### System Extension in "Waiting for User" State

**Symptoms:**
- Extension shows as "awaiting user approval"
- No notification appears

**Solutions:**

1. **Check System Settings:**
   - System Settings → Privacy & Security
   - Scroll to Security section
   - Look for pending approval

2. **Open notification manually:**
   - Open Notification Center
   - Look for system extension approval

3. **Force approval with developer mode:**
   ```bash
   sudo systemextensionsctl developer on
   sudo systemextensionsctl list
   ```

4. **Reset and reinstall:**
   ```bash
   sudo systemextensionsctl reset
   sudo reboot
   sudo make install
   ```

### Driver Loaded but Not Active

**Symptoms:**
- Extension shows in list but marked as inactive
- Device not recognized

**Solutions:**

1. **Check driver status:**
   ```bash
   systemextensionsctl list | grep RTL8814AU
   ```

2. **View driver logs:**
   ```bash
   log stream --predicate 'subsystem == "com.opensource.RTL8814AUDriver"' \
              --level debug
   ```

3. **Verify device connection:**
   ```bash
   system_profiler SPUSBDataType | grep -A 10 "Realtek"
   ```

4. **Restart with device connected:**
   - Connect the USB adapter
   - Restart your Mac
   - Check if driver activates

---

## Device Recognition Issues

### USB Device Not Detected

**Symptoms:**
- Driver loads but device not recognized
- No entry in `system_profiler SPUSBDataType`

**Solutions:**

1. **Check USB connection:**
   - Try different USB ports
   - Try USB 3.0 vs USB 2.0 ports
   - Check cable and adapter condition

2. **Verify device power:**
   - Some adapters need external power
   - Try powered USB hub

3. **Check USB bus:**
   ```bash
   system_profiler SPUSBDataType
   ```
   Look for any Realtek devices

4. **Reset USB system:**
   ```bash
   sudo killall -STOP -c usbd
   sleep 2
   sudo killall -CONT -c usbd
   ```

### Wrong Product ID

**Symptoms:**
- Device appears in USB list but driver doesn't claim it
- Vendor ID is 0x0bda but wrong product ID

**Solutions:**

1. **Check supported IDs:**
   Current supported product IDs:
   - 0x8813 (primary)
   - 0x8834 (alternative)

2. **Add your product ID:**
   Edit `RTL8814AUDriver/Info.plist` and add:
   ```xml
   <key>RTL8814AU_USB_Driver_Custom</key>
   <dict>
       <key>idVendor</key>
       <integer>3034</integer>  <!-- 0x0bda -->
       <key>idProduct</key>
       <integer>YOUR_DECIMAL_PRODUCT_ID</integer>
       <!-- Add other required keys -->
   </dict>
   ```

3. **Rebuild and reinstall:**
   ```bash
   make clean build install
   ```

### Firmware Load Failure

**Symptoms:**
- Device recognized but not functional
- Logs show firmware errors

**Solutions:**

1. **Check firmware file:**
   ```bash
   ls -l RTL8814AUDriver/Firmware/
   ```

2. **Download correct firmware:**
   ```bash
   # From Linux firmware repository
   curl -o RTL8814AUDriver/Firmware/rtl8814au_fw.bin \
        https://git.kernel.org/pub/scm/linux/kernel/git/firmware/linux-firmware.git/plain/rtlwifi/rtl8814aufw.bin
   ```

3. **Verify firmware format:**
   ```bash
   hexdump -C RTL8814AUDriver/Firmware/rtl8814au_fw.bin | head
   ```

4. **Rebuild with firmware:**
   ```bash
   make clean build install
   ```

---

## Connection Problems

### Network Interface Not Appearing

**Symptoms:**
- Driver loaded, device recognized
- No new network interface in `ifconfig`

**Solutions:**

1. **Check interface list:**
   ```bash
   ifconfig -a
   networksetup -listallhardwareports
   ```

2. **View driver logs:**
   ```bash
   log stream --predicate 'subsystem == "com.opensource.RTL8814AUDriver"'
   ```

3. **Manually create interface (advanced):**
   ```bash
   sudo ifconfig enX create  # X = interface number
   sudo ifconfig enX up
   ```

4. **Check network service:**
   ```bash
   networksetup -listallnetworkservices
   ```

### Cannot Scan for WiFi Networks

**Symptoms:**
- Interface exists but can't scan
- No networks visible

**Solutions:**

1. **Enable interface:**
   ```bash
   sudo ifconfig en7 up  # Replace en7 with your interface
   ```

2. **Scan manually:**
   ```bash
   sudo wdutil diagnose
   ```

3. **Check radio state:**
   ```bash
   sudo wdutil info
   ```

4. **Reset interface:**
   ```bash
   sudo ifconfig en7 down
   sleep 2
   sudo ifconfig en7 up
   ```

### Connection Drops Frequently

**Symptoms:**
- Connects but drops after short time
- Unstable connection

**Solutions:**

1. **Check signal strength:**
   ```bash
   sudo wdutil info | grep RSSI
   ```

2. **Disable power management:**
   ```bash
   sudo pmset -a disksleep 0
   ```

3. **Check for interference:**
   - Move closer to router
   - Change WiFi channel
   - Avoid USB 3.0 interference

4. **Update router firmware:**
   - Check for router updates
   - Adjust router settings

---

## Performance Issues

### Slow Transfer Speeds

**Symptoms:**
- Connection works but speeds are low
- High latency

**Solutions:**

1. **Check link speed:**
   ```bash
   ifconfig en7 | grep media
   ```

2. **Optimize MTU:**
   ```bash
   sudo ifconfig en7 mtu 1500
   ```

3. **Disable power saving:**
   ```bash
   sudo pmset -a powernap 0
   ```

4. **Check CPU usage:**
   ```bash
   top -o cpu | grep RTL8814AU
   ```

### High CPU Usage

**Symptoms:**
- Driver consumes excessive CPU
- System becomes slow

**Solutions:**

1. **Check driver process:**
   ```bash
   ps aux | grep RTL8814AU
   top -o cpu
   ```

2. **View detailed logs:**
   ```bash
   log show --predicate 'subsystem == "com.opensource.RTL8814AUDriver"' \
            --last 5m \
            --debug
   ```

3. **Reduce logging level:**
   Edit driver code to reduce debug logging

4. **Report issue:**
   - Collect performance data
   - File issue on GitHub

---

## Build and Signing Issues

### Build Fails with Errors

**Symptoms:**
- `xcodebuild` or `make build` fails
- Compilation errors

**Solutions:**

1. **Check Xcode version:**
   ```bash
   xcodebuild -version
   ```
   Requires Xcode 16.0+

2. **Update Swift:**
   ```bash
   swift --version
   ```

3. **Clean build:**
   ```bash
   make clean
   rm -rf DerivedData
   make build
   ```

4. **Check for syntax errors:**
   ```bash
   swift build --dry-run
   ```

### Code Signing Fails

**Symptoms:**
- `codesign` command fails
- "No identity found" error

**Solutions:**

1. **List signing identities:**
   ```bash
   security find-identity -v -p codesigning
   ```

2. **Install certificate:**
   - Sign in to developer.apple.com
   - Download "Developer ID Application" certificate
   - Double-click to install in Keychain

3. **Set identity:**
   ```bash
   export CODESIGN_IDENTITY="Developer ID Application: Your Name (TEAM_ID)"
   ./sign.sh
   ```

4. **Check certificate validity:**
   ```bash
   security find-certificate -c "Developer ID Application"
   ```

### Entitlements Issues

**Symptoms:**
- Driver builds but won't load
- Entitlement verification fails

**Solutions:**

1. **Verify entitlements file:**
   ```bash
   plutil -lint RTL8814AUDriver/RTL8814AUDriver.entitlements
   ```

2. **Check applied entitlements:**
   ```bash
   codesign -d --entitlements :- build/RTL8814AUDriver.dext
   ```

3. **Compare with requirements:**
   Required entitlements:
   - `com.apple.developer.driverkit`
   - `com.apple.developer.driverkit.transport.usb`
   - Others (see entitlements file)

---

## System Extension Issues

### "System Extension Blocked" Message

**Symptoms:**
- System blocks extension loading
- Security prompt appears

**Solutions:**

1. **Allow in System Settings:**
   - System Settings → Privacy & Security
   - Click "Allow" button

2. **Check team ID:**
   ```bash
   codesign -dvv build/RTL8814AUDriver.dext | grep TeamIdentifier
   ```

3. **Verify notarization** (for distribution):
   ```bash
   spctl --assess --type install build/RTL8814AUDriver.dext
   ```

### Multiple Versions Installed

**Symptoms:**
- Multiple entries in `systemextensionsctl list`
- Conflicts between versions

**Solutions:**

1. **List all versions:**
   ```bash
   systemextensionsctl list
   ```

2. **Uninstall all:**
   ```bash
   sudo systemextensionsctl reset
   ```

3. **Clean install:**
   ```bash
   sudo reboot
   # After reboot:
   sudo make install
   ```

---

## Diagnostic Commands

### Complete System Check

```bash
#!/bin/bash

echo "=== System Information ==="
sw_vers

echo -e "\n=== SIP Status ==="
csrutil status

echo -e "\n=== System Extensions ==="
systemextensionsctl list | grep -E "(System|RTL8814AU)"

echo -e "\n=== USB Devices ==="
system_profiler SPUSBDataType | grep -A 10 "Realtek"

echo -e "\n=== Network Interfaces ==="
ifconfig | grep -E "^(en|wlan)"

echo -e "\n=== Driver Logs (last 10 minutes) ==="
log show --predicate 'subsystem == "com.opensource.RTL8814AUDriver"' \
         --last 10m \
         --info

echo -e "\n=== Network Services ==="
networksetup -listallhardwareports

echo -e "\n=== WiFi Information ==="
sudo wdutil info 2>/dev/null || echo "Not available"
```

Save this as `diagnostic.sh` and run:
```bash
chmod +x diagnostic.sh
./diagnostic.sh > diagnostic_report.txt
```

### Log Collection

```bash
# Collect all relevant logs
log collect --last 1h --output driver_logs.logarchive

# Export system extension logs
log show --archive driver_logs.logarchive \
         --predicate 'subsystem == "com.apple.SystemExtensions"' \
         > system_extensions.log

# Export driver logs
log show --archive driver_logs.logarchive \
         --predicate 'subsystem == "com.opensource.RTL8814AUDriver"' \
         --debug \
         > driver_debug.log
```

---

## Getting More Help

If none of these solutions work:

1. **Collect diagnostic information:**
   ```bash
   ./diagnostic.sh > report.txt
   ```

2. **Check GitHub Issues:**
   Search for similar problems:
   https://github.com/yourusername/rtl8814au-macos/issues

3. **Create new issue:**
   Include:
   - macOS version
   - Driver version
   - Diagnostic report
   - Steps to reproduce
   - Expected vs actual behavior

4. **Join discussions:**
   https://github.com/yourusername/rtl8814au-macos/discussions

---

## Emergency Recovery

### Complete Driver Removal

```bash
# Uninstall system extension
sudo systemextensionsctl uninstall com.opensource.RTL8814AUDriver com.opensource.RTL8814AUDriver

# Remove all files
sudo rm -rf /Library/SystemExtensions/*/com.opensource.RTL8814AUDriver.dext

# Reset system extension database
sudo systemextensionsctl reset

# Restart
sudo reboot
```

### Reset to Clean State

```bash
# Complete cleanup
sudo systemextensionsctl reset
sudo rm -rf /Library/SystemExtensions/*
sudo rm -rf ~/Library/SystemExtensions/*
sudo reboot
```

**Warning:** This removes ALL system extensions, not just the driver!

---

Last updated: December 27, 2025
