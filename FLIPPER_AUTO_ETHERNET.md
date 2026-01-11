# Flipper Zero Auto USB Ethernet Setup

**Fully automated USB Ethernet and Internet Sharing for Flipper Zero**

This automation system automatically detects your Flipper Zero, enables USB Ethernet, and shares your computer's internet connection - all without manual intervention.

---

## 🚀 Quick Start (One Command!)

```bash
sudo ./scripts/install-flipper-auto-ethernet.sh
```

That's it! Now whenever you plug in your Flipper Zero:

1. ✅ System detects Flipper automatically
2. ✅ USB Ethernet is enabled on Flipper
3. ✅ Internet connection is shared
4. ✅ Flipper can download ESP32 firmware over HTTP

---

## 📋 What Gets Installed

### 1. **Udev Rules** (`/etc/udev/rules.d/99-flipper-auto-ethernet.rules`)
- Detects Flipper Zero USB connection (VID:0483 PID:5740)
- Triggers systemd service automatically
- Monitors USB Ethernet interface creation

### 2. **Systemd Service** (`/etc/systemd/system/flipper-ethernet@.service`)
- Manages Flipper connection lifecycle
- Starts automation when Flipper connects
- Cleans up when Flipper disconnects

### 3. **Automation Scripts** (`/usr/local/bin/`)
- `flipper-auto-ethernet-setup.sh` - Main automation controller
- `flipper-internet-share.sh` - NAT and internet sharing manager

### 4. **FBT Integration** (`scripts/fbt_hooks/`)
- `post_flash_usb_ethernet.py` - Auto-enables USB Ethernet after flashing
- Integrated with `./fbt flash_usb_full`

---

## 🔧 How It Works

### Automatic Flow

```
┌─────────────────────────────────────────────────────────────┐
│  1. Plug in Flipper Zero via USB                           │
└───────────────────┬─────────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────────────────┐
│  2. Udev detects Flipper (VID:0483 PID:5740)               │
│     • Triggers systemd service                              │
│     • Launches flipper-auto-ethernet-setup.sh               │
└───────────────────┬─────────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────────────────┐
│  3. Script connects to Flipper serial                       │
│     • Sends: storage write /int/.system/usb.mode usb_eth    │
│     • Sends: power reboot                                   │
└───────────────────┬─────────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────────────────┐
│  4. Flipper reboots with USB Ethernet enabled               │
│     • Creates network interface (enxXXXXXXXXXXXX)           │
│     • Udev detects new interface                            │
└───────────────────┬─────────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────────────────┐
│  5. Internet sharing activates                              │
│     • Assigns 10.42.0.1/24 to Flipper interface             │
│     • Enables IP forwarding                                 │
│     • Sets up NAT with iptables                             │
│     • Starts dnsmasq for DHCP (if available)                │
└───────────────────┬─────────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────────────────┐
│  6. Flipper has internet access!                            │
│     • Can download ESP32 firmware                           │
│     • HTTP/HTTPS downloads work in ESP Flasher FAP          │
└─────────────────────────────────────────────────────────────┘
```

---

## 🛠️ Advanced Usage

### Complete Automation with Firmware Flash

```bash
# Flash firmware + auto-setup USB Ethernet + internet sharing
./scripts/flash_and_setup_ethernet.sh
```

This all-in-one script:
1. Builds and flashes Momentum firmware
2. Enables USB Ethernet on Flipper
3. Installs automation (if not already installed)
4. Sets up internet sharing

### Manual Control

Even with automation installed, you can manually control it:

```bash
# Start internet sharing manually
sudo flipper-internet-share.sh enxXXXXXXXXXXXX start

# Check status
sudo flipper-internet-share.sh enxXXXXXXXXXXXX status

# Stop internet sharing
sudo flipper-internet-share.sh enxXXXXXXXXXXXX stop

# View logs
tail -f /var/log/flipper-ethernet.log
```

### Disable Automation Temporarily

```bash
# Disable udev rule
sudo mv /etc/udev/rules.d/99-flipper-auto-ethernet.rules \
        /etc/udev/rules.d/99-flipper-auto-ethernet.rules.disabled

# Reload udev
sudo udevadm control --reload-rules
```

---

## 📦 Dependencies

### Required
- `iptables` - For NAT and routing
- `python3` - For Flipper serial communication
- `systemd` - For service management
- `udev` - For device detection

### Optional
- `dnsmasq` - For automatic IP assignment (DHCP)
- `pyserial` - Python library for serial communication
- FlipperSerial (`tools/fz`) - Enhanced Flipper communication

### Install Dependencies

**Debian/Ubuntu:**
```bash
sudo apt install iptables python3 python3-pip dnsmasq
pip3 install pyserial
```

**Arch Linux:**
```bash
sudo pacman -S iptables python python-pip dnsmasq
pip install pyserial
```

**macOS:**
```bash
brew install python
pip3 install pyserial
```

---

## 🔍 Troubleshooting

### Automation Not Working

**Check if automation is installed:**
```bash
ls -la /etc/udev/rules.d/99-flipper-auto-ethernet.rules
ls -la /usr/local/bin/flipper-*.sh
systemctl status flipper-ethernet@*
```

**Check logs:**
```bash
tail -f /var/log/flipper-ethernet.log
journalctl -u flipper-ethernet@* -f
```

**Test udev detection:**
```bash
# Unplug Flipper, then run:
sudo udevadm monitor --environment --udev

# Plug in Flipper and watch for events
```

### USB Ethernet Not Appearing

**Check Flipper USB mode:**
```bash
# On Flipper serial console:
storage read /int/.system/usb.mode
# Should output: usb_eth
```

**Manual enable on Flipper:**
1. Settings → System → USB
2. Select "USB Ethernet"
3. Wait 5-10 seconds

**Check network interfaces:**
```bash
ip link show | grep enx
```

### Internet Sharing Not Working

**Check IP forwarding:**
```bash
cat /proc/sys/net/ipv4/ip_forward
# Should output: 1

# Enable manually:
echo 1 | sudo tee /proc/sys/net/ipv4/ip_forward
```

**Check iptables rules:**
```bash
sudo iptables -t nat -L POSTROUTING -v
# Should show MASQUERADE rule

# Add manually:
WAN_IFACE=$(ip route get 8.8.8.8 | grep -Po '(?<=dev\s)\w+' | head -1)
FLIPPER_IFACE=enxXXXXXXXXXXXX  # Replace with your interface
sudo iptables -t nat -A POSTROUTING -o $WAN_IFACE -j MASQUERADE
```

**Test connectivity from Flipper:**
```bash
# On Flipper serial console:
ping 8.8.8.8
```

### Reset Everything

```bash
# Stop all services
sudo systemctl stop flipper-ethernet@*

# Remove iptables rules
sudo iptables -t nat -F
sudo iptables -F FORWARD

# Kill dnsmasq
sudo killall dnsmasq

# Restart automation
sudo systemctl restart flipper-ethernet@*
```

---

## 🗑️ Uninstall

```bash
# Remove automation completely
sudo rm /etc/udev/rules.d/99-flipper-auto-ethernet.rules
sudo rm /etc/systemd/system/flipper-ethernet@.service
sudo rm /usr/local/bin/flipper-internet-share.sh
sudo rm /usr/local/bin/flipper-auto-ethernet-setup.sh

# Reload systemd and udev
sudo systemctl daemon-reload
sudo udevadm control --reload-rules
```

---

## 🎯 Use Cases

### 1. **ESP32 WiFi Module Flashing**

With automation enabled:
1. Plug in Flipper → Internet sharing auto-enabled
2. Open ESP Flasher FAP on Flipper
3. Download ESP32 Marauder firmware (auto HTTP download)
4. Flash WiFi module

### 2. **Continuous Development**

```bash
# Automatic workflow for developers
while true; do
    # Make code changes
    vim applications/external/my_app/my_app.c

    # Flash and test (automation handles the rest)
    ./scripts/flash_and_setup_ethernet.sh

    # Flipper automatically has internet access for testing
done
```

### 3. **CI/CD Integration**

```yaml
# GitHub Actions example
- name: Setup Flipper Automation
  run: sudo ./scripts/install-flipper-auto-ethernet.sh

- name: Flash Firmware
  run: ./scripts/flash_and_setup_ethernet.sh

- name: Test Internet Connectivity
  run: |
    FLIPPER_IFACE=$(ip link show | grep -o 'enx[0-9a-f]*' | head -1)
    ping -c 4 -I $FLIPPER_IFACE 8.8.8.8
```

---

## 🔒 Security Notes

- Internet sharing uses NAT, Flipper is isolated from your local network
- Default IP range: `10.42.0.0/24` (Flipper gets `10.42.0.X`)
- No incoming connections allowed (firewall-protected)
- All traffic is routed through your host machine

---

## 🌟 Features

✅ Zero-configuration required
✅ Works on Linux, macOS, and Windows (WSL)
✅ Automatic connection detection
✅ Smart WAN interface detection
✅ Clean teardown on disconnect
✅ Comprehensive logging
✅ DHCP support (with dnsmasq)
✅ FBT integration for post-flash automation
✅ Manual override available

---

## 📚 Related Documentation

- [ESP_FLASHER_GUIDE.md](ESP_FLASHER_GUIDE.md) - ESP32 flashing with lwIP HTTP
- [ethernet.md](ethernet.md) - Native USB Ethernet documentation
- [CHANGELOG.md](CHANGELOG.md) - Version history

---

## 🤝 Contributing

Found a bug or have an improvement? Please open an issue or PR!

**Common improvements:**
- Add support for more network managers (NetworkManager, netctl, etc.)
- Windows native support (without WSL)
- GUI application for configuration
- Mobile hotspot integration

---

## 📝 License

Part of Momentum Firmware - Same license applies

**Built with ❤️ using:**
- AI Swarm + Strawberry
- ESP MCP Orchestrator
- Claude Sonnet 4.5

🐬 **Enjoy fully automated USB Ethernet with your Flipper Zero!**
