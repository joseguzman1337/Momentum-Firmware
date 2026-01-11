# ESP Flasher FAP - lwIP HTTP Download Guide

## ✅ Completed Setup

### 1. Fixed Broken External Apps
- Fixed `multi_counter` mutex pointer issue (FuriMutex** → FuriMutex*)
- Fixed `hc11_modem` icon header includes
- Removed incompatible apps: `deadzone`, `secret_toggle`, `smack_my_dolphin_up`, `mifare_nested`, `canfdhs`
- Successfully built firmware with **all working external apps** + ESP Flasher FAP

### 2. Firmware Flashed
- ✅ Built Momentum firmware (commit 1ac3dd47)
- ✅ Flashed via `./fbt flash_usb_full`
- ✅ Flipper Zero rebooted successfully
- ✅ ESP Flasher FAP included with lwIP HTTP download support

### 3. USB Ethernet Detected
Flipper Zero USB Ethernet interfaces detected:
- `enx50ebf649e88a`
- `enxc8a3622ca772`

---

## 🌐 Enable Internet Connection Sharing

### ⚡ Automatic Setup (Recommended)

**One-time installation for full automation:**

```bash
sudo ./scripts/install-flipper-auto-ethernet.sh
```

This installs automation that automatically:
1. Detects when Flipper Zero is plugged in
2. Enables USB Ethernet on Flipper
3. Sets up internet sharing via NAT
4. Cleans up on disconnect

**After installation, just plug in your Flipper and everything works automatically!**

See [FLIPPER_AUTO_ETHERNET.md](FLIPPER_AUTO_ETHERNET.md) for full automation documentation.

---

## 🔁 Auto Flash WiFi Devboard (Host-Side, via fbt)

If you want to update the WiFi devboard firmware directly from your computer:

```bash
./fbt devboard_flash ARGS="--wait --timeout 180 --auto-bootloader"
```

Or use the full automation wrapper:

```bash
./scripts/flash_and_setup_ethernet.sh --devboard-flash
```

Notes:
1. `--auto-bootloader` is best-effort and depends on the USB serial wiring.
2. `--wait` keeps polling until the board is detected.
3. Use `--devboard-channel dev` or `--devboard-channel rc` if needed.

---

### 🔧 Manual Setup (If automation not installed)

```bash
sudo bash scripts/enable_internet.sh
```

This script will:
1. Detect your WAN interface (e.g., `enp0s20f0u1u2c2`)
2. Enable IP forwarding
3. Set up NAT (Network Address Translation)
4. Configure iptables for the Flipper's USB Ethernet

---

## 📡 Using ESP Flasher FAP with lwIP HTTP Download

### Method 1: Auto-Download ESP32 Marauder (Recommended for WiFi Devboard S2)

The ESP Flasher app can automatically download the latest ESP32 Marauder firmware:

**On your Flipper Zero:**

1. **Enable USB Ethernet**:
   - Settings → System → USB → Select "USB Ethernet"
   - Wait for connection (~5-10 seconds)

2. **Launch ESP Flasher**:
   - Apps → GPIO → [ESP] ESP Flasher

3. **Download Firmware** (if supported in UI):
   - The app will automatically download from:
     - `https://github.com/justcallmekoko/ESP32Marauder/releases/latest/download/`

   Files downloaded to `/ext/apps_data/esp_flasher/assets/marauder/s2/`:
   - Bootloader: `esp32_marauder.ino.bootloader.bin` (→ 0x1000)
   - Partitions: `esp32_marauder.ino.partitions.bin` (→ 0x8000)
   - Boot App0: `boot_app0.bin` (→ 0xE000)
   - Firmware: `esp32_marauder.flipper.bin` (→ 0x10000)

4. **Flash the WiFi Module**:
   - Connect WiFi Devboard to Flipper
   - Press and hold BOOT button
   - Press RESET button once
   - Release BOOT after 2 seconds
   - In ESP Flasher: Select "Flash ESP"
   - Choose the downloaded files
   - Press "[>] FLASH"
   - Wait for completion (~2-3 minutes)

### Method 2: Manual HTTP Download

If you need to download other ESP32 firmware:

**lwIP HTTP Download Function:**
```c
bool furi_hal_usb_eth_http_download_to_file(
    const char* url,      // Full HTTP/HTTPS URL
    const char* dest_path, // Destination file path on SD card
    uint32_t timeout_ms   // Timeout in milliseconds (60000 = 1 min)
);
```

**Example URLs for different ESP32 targets:**
- ESP32: `https://github.com/.../firmware_esp32.bin`
- ESP32-S2: `https://github.com/.../firmware_s2.bin`
- ESP32-S3: `https://github.com/.../firmware_s3.bin`
- ESP32-C3: `https://github.com/.../firmware_c3.bin`

---

## 🔧 Flash Addresses for Different ESP32 Chips

### WiFi Devboard (ESP32-S2)
```
0x1000  - Bootloader
0x8000  - Partition Table
0xE000  - Boot App0
0x10000 - Firmware
```

### ESP32 (Classic)
```
0x1000  - Bootloader
0x8000  - Partition Table
0xE000  - Boot App0
0x10000 - Firmware
```

### ESP32-C3/S3
```
0x0     - Bootloader
0x8000  - Partition Table
0x10000 - Firmware
```

---

## 🛠️ AI Infrastructure Available

### ESP MCP Server (.ai/mcp/servers/esp_mcp/)
```bash
# Build ESP-IDF projects
esp_mcp build_esp_project --project-path <path>

# Flash ESP devices
esp_mcp flash_esp_project --project-path <path> --port /dev/ttyUSB0

# List serial ports
esp_mcp list_esp_serial_ports
```

### ESP MCP Orchestrator (.ai/esp_mcp_orchestrator/)
Rust orchestrator for ESP MCP operations (already built).

### Strawberry AI (.ai/strawberry/)
Hallucination detection for AI-generated code verification.

---

## 📝 Next Steps

1. **Enable Internet Sharing** (see command above)
2. **On Flipper**: Enable USB Ethernet in Settings
3. **Launch ESP Flasher** and download/flash firmware
4. **Verify** WiFi module functionality

---

## 🐛 Troubleshooting

**Flipper can't access internet:**
```bash
# Check if NAT is enabled
sudo iptables -t nat -L POSTROUTING
# Should show MASQUERADE rule

# Check IP forwarding
cat /proc/sys/net/ipv4/ip_forward
# Should return: 1

# Re-run setup
sudo bash scripts/enable_internet.sh
```

**USB Ethernet not detected:**
1. Reconnect Flipper USB cable
2. On Flipper: Settings → System → Reboot
3. Select USB Ethernet after reboot

**HTTP download fails:**
1. Verify internet sharing is enabled
2. Check Flipper's USB Ethernet connection
3. Try pinging from Flipper (if CLI available)
4. Verify URL is accessible from host computer

---

## 📚 References

- ESP Flasher FAP: `applications/external/esp_flasher/`
- HTTP Module: `esp_flasher_http.c` (lwIP implementation)
- ESP32 Marauder: https://github.com/justcallmekoko/ESP32Marauder
- Momentum Firmware: https://github.com/Next-Flip/Momentum-Firmware

**Built with:**
- Momentum Firmware next-1ac3dd47
- AI Swarm + Strawberry
- ESP MCP Orchestrator
- Claude Sonnet 4.5
