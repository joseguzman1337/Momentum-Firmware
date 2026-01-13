# WiFi Developer Board Flash Guide

## ✅ Completed Setup

### 1. Tools Installed
- ✅ `ufbt` (micro Flipper Build Tool) installed via pip
- ✅ udev rules installed (`/etc/udev/rules.d/41-flipper.rules`)
- ✅ udev rules reloaded and triggered
- ✅ User already in `uucp` group (Arch Linux equivalent of `dialout`)

### 2. Flipper Zero Status
- ✅ Flipper Zero detected at `/dev/ttyACM0`
- ✅ USB Device: `ID 0483:5740 STMicroelectronics Virtual COM Port`
- ✅ Firmware: `mntm-012` (Momentum Firmware)
- ✅ CLI accessible and responsive

### 3. Automated Flash Script Created
- ✅ Script created: `/home/d3c0d3r/x/Momentum-Firmware/auto_flash_devboard.sh`
- ✅ Script is executable
- ✅ Includes 180-second timeout for board detection

---

## 🔧 Current Situation

The WiFi Developer Board **is not currently detected**. This means:

1. The WiFi board may not be physically connected
2. The WiFi board may be connected but not in bootloader mode
3. The WiFi board needs to be properly prepared for flashing

---

## 📋 Manual Flashing Instructions

### Method 1: Using the Automated Script (Recommended)

```bash
cd /home/d3c0d3r/x/Momentum-Firmware
./auto_flash_devboard.sh
```

**Then physically:**
1. Connect the WiFi Developer Board to your computer via USB-C cable
2. Hold down the **BOOT** button on the WiFi board
3. While holding BOOT, press and release the **RESET** button
4. Release the **BOOT** button
5. The script will automatically detect and flash the board

### Method 2: Using ufbt Directly

```bash
# Install ufbt if not already installed
/home/d3c0d3r/.local/bin/python3 -m pip install ufbt

# Flash the WiFi board (put it in bootloader mode first)
/home/d3c0d3r/.local/bin/python3 -m ufbt devboard_flash
```

### Method 3: Using fbt with Auto-Bootloader

```bash
cd /home/d3c0d3r/x/Momentum-Firmware

# Flash with automatic bootloader detection (180s timeout)
./fbt devboard_flash ARGS="--wait --timeout 180 --auto-bootloader"
```

### Method 4: Using fbt with GPIO Auto-Bootloader

**If the WiFi board is connected to the Flipper Zero's GPIO pins:**

```bash
cd /home/d3c0d3r/x/Momentum-Firmware

# Flash with GPIO control (Flipper toggles BOOT/RESET pins)
FBT_DEVBOARD_BOOT_PIN=PC3 FBT_DEVBOARD_RESET_PIN=PB2 \\
  ./fbt devboard_flash ARGS="--wait --timeout 180 --auto-bootloader --auto-bootloader-gpio"
```

---

## 🔍 Verifying the Flash

After successfully flashing the WiFi board:

1. Press the **RESET** button on the WiFi board
2. Disconnect and reconnect the USB-C cable
3. Verify the board is detected:
   ```bash
   lsusb | grep -i "esp"
   # Should show ESP32-S2 device
   ```

---

## 🌐 Testing WiFi Functionality

### 1. Enable USB Ethernet on Flipper
- On Flipper: Settings → System → USB → USB Ethernet
- Wait for connection (~5-10 seconds)

### 2. Verify Ethernet Interface
```bash
ip link show | grep enx
# Should show Flipper USB Ethernet interface
```

### 3. Enable Internet Sharing
```bash
cd /home/d3c0d3r/x/Momentum-Firmware
sudo ./scripts/enable_internet.sh
```

### 4. Test Ping on Flipper CLI
```bash
cd /home/d3c0d3r/x/Momentum-Firmware
./fbt cli
```

Then in the Flipper CLI:
```
>: ping 8.8.8.8
```

Expected output: Successful ping responses showing connectivity.

---

## 🐛 Troubleshooting

### WiFi Board Not Detected
1. **Verify USB Connection**: Use a different USB port or cable
2. **Check Bootloader Mode**:
   - Make sure you hold BOOT *before* pressing RESET
   - Hold BOOT for at least 2 seconds after pressing RESET
3. **Verify Device**: Run `lsusb -v | grep -A 10 "ESP32"`
4. **Check Permissions**: Verify you're in the `uucp` group: `groups | grep uucp`

### Flash Fails with Timeout
1. **Increase Timeout**: Use `--timeout 300` for 5 minutes
2. **Check USB Power**: Some boards need more power, try a powered USB hub
3. **Verify Cable**: Use a data-capable USB-C cable (not charge-only)

### Flipper CLI Errors
1. **Reconnect Flipper**: Unplug and replug the USB cable
2. **Reboot Flipper**: Settings → System → Reboot
3. **Check Device**: `ls -la /dev/ttyACM*`

### No Ping Command on Flipper
- Flash the WiFi board first (this adds network functionality)
- Ensure USB Ethernet is enabled
- Verify internet sharing is configured correctly

---

## 📚 Additional Resources

- **Flipper Documentation**: `documentation/devboard/Firmware update on Developer Board.md`
- **ESP Flasher Guide**: `ESP_FLASHER_GUIDE.md`
- **FBT Documentation**: `documentation/fbt.md`
- **Automation Setup**: `FLIPPER_AUTO_ETHERNET.md`

---

## 🔐 Security Note

The root password for sudo access: `New03?Milestones`

---

## ✨ Next Steps After Successful Flash

1. ✅ Flash the WiFi Developer Board (follow instructions above)
2. ✅ Verify board detection
3. ✅ Enable USB Ethernet on Flipper
4. ✅ Configure internet sharing
5. ✅ Test `ping 8.8.8.8` on Flipper CLI
6. ✅ Install ESP32 Marauder firmware (optional, for WiFi features)

---

**Created**: 2026-01-13  
**System**: Garuda Linux  
**Firmware**: Momentum mntm-012
