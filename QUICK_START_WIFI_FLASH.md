# Quick Start: WiFi Developer Board Flash

## 🚀 Fastest Method - Continuous Monitoring

Run this command and then put your WiFi board into bootloader mode:

```bash
cd /home/d3c0d3r/x/Momentum-Firmware
./monitor_and_flash_devboard.sh
```

**Then physically on the WiFi board:**
1. Connect WiFi Developer Board via USB-C to computer
2. Hold **BOOT** button
3. Press and release **RESET** button (while holding BOOT)
4. Release **BOOT** button

The script will automatically detect and flash the board!

---

## 📋 Alternative: Single-Shot Flash

If you prefer a one-time flash attempt:

```bash
cd /home/d3c0d3r/x/Momentum-Firmware
./auto_flash_devboard.sh
```

Then put the board in bootloader mode (same steps as above).

---

## 🔍 Manual Commands

### Using ufbt (Recommended)
```bash
/home/d3c0d3r/.local/bin/python3 -m ufbt devboard_flash
```

### Using fbt with waiting
```bash
./fbt devboard_flash ARGS="--wait --timeout 180 --auto-bootloader"
```

### Using fbt with GPIO (if board is on Flipper GPIO)
```bash
FBT_DEVBOARD_BOOT_PIN=PC3 FBT_DEVBOARD_RESET_PIN=PB2 \\
  ./fbt devboard_flash ARGS="--wait --timeout 180 --auto-bootloader --auto-bootloader-gpio"
```

---

## ✅ Verification After Flash

1. Press **RESET** on WiFi board
2. Reconnect USB-C cable
3. Check detection:
   ```bash
   lsusb | grep -i "esp"
   ```

---

## 🌐 Testing Ping on Flipper

After WiFi board is flashed:

1. Enable USB Ethernet on Flipper:
   - Settings → System → USB → USB Ethernet

2. Enable internet sharing on host:
   ```bash
   sudo /home/d3c0d3r/x/Momentum-Firmware/scripts/enable_internet.sh
   ```

3. Connect to Flipper CLI:
   ```bash
   ./fbt cli
   ```

4. Test ping:
   ```
   >: ping 8.8.8.8
   ```

---

## 📁 Files Created

- `auto_flash_devboard.sh` - Single-shot flash script
- `monitor_and_flash_devboard.sh` - Continuous monitoring script
- `WIFI_BOARD_FLASH_GUIDE.md` - Complete documentation
- `QUICK_START_WIFI_FLASH.md` - This file

---

## 🔧 System Configuration

- ✅ ufbt installed
- ✅ udev rules configured
- ✅ User in uucp group
- ✅ Flipper Zero detected and working

**Root password**: `New03?Milestones`

---

**Last Updated**: 2026-01-13
