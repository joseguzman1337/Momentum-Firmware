# ⚡ Quick Start: Automated USB Ethernet

**Get your Flipper Zero online in 30 seconds!**

---

## 🎯 One-Time Setup

```bash
cd /home/d3c0d3r/x/Momentum-Firmware
sudo ./scripts/install-flipper-auto-ethernet.sh
```

**That's it!** Automation is now installed.

---

## 🔌 Daily Usage

From now on, just **plug in your Flipper Zero** and:

1. ✅ System detects Flipper automatically
2. ✅ USB Ethernet is enabled on Flipper
3. ✅ Internet connection is shared
4. ✅ Ready to download ESP32 firmware!

**No manual steps required!**

---

## 🚀 Flash Firmware + Auto Setup

All-in-one command:

```bash
./scripts/flash_and_setup_ethernet.sh
```

This will:
1. Build and flash Momentum firmware
2. Enable USB Ethernet on Flipper
3. Set up internet sharing
4. Install automation (if not already installed)

---

## 📱 Using ESP Flasher FAP

After automation is installed:

1. **Plug in Flipper** (wait 10 seconds for auto-setup)
2. **On Flipper:** Apps → GPIO → [ESP] ESP Flasher
3. **Select:** Download ESP32 Marauder
4. **Flash** your WiFi module

**HTTP downloads work automatically over USB Ethernet!**

---

## 🔍 Quick Status Check

```bash
# View automation logs
tail -f /var/log/flipper-ethernet.log

# Check if running
systemctl status flipper-ethernet@*

# Check network interface
ip addr show | grep enx
```

---

## ⚙️ Manual Control (Optional)

Even with automation, you can control it manually:

```bash
# Start manually
sudo flipper-internet-share.sh enxXXXXXXXXXXXX start

# Stop
sudo flipper-internet-share.sh enxXXXXXXXXXXXX stop

# Status
sudo flipper-internet-share.sh enxXXXXXXXXXXXX status
```

---

## 🛠️ Troubleshooting

### USB Ethernet not appearing?

**On Flipper:**
1. Settings → System → USB
2. Select "USB Ethernet"
3. Wait 10 seconds

### Internet not working?

```bash
# Check IP forwarding
cat /proc/sys/net/ipv4/ip_forward
# Should show: 1

# Check NAT rules
sudo iptables -t nat -L POSTROUTING
# Should show MASQUERADE

# Re-run setup
sudo flipper-internet-share.sh <interface> start
```

### Need more help?

See full documentation: [FLIPPER_AUTO_ETHERNET.md](FLIPPER_AUTO_ETHERNET.md)

---

## 🗑️ Uninstall (if needed)

```bash
sudo rm /etc/udev/rules.d/99-flipper-auto-ethernet.rules
sudo rm /etc/systemd/system/flipper-ethernet@.service
sudo rm /usr/local/bin/flipper-*.sh
sudo systemctl daemon-reload
sudo udevadm control --reload-rules
```

---

## 📚 Documentation

- **Full Automation Guide:** [FLIPPER_AUTO_ETHERNET.md](FLIPPER_AUTO_ETHERNET.md)
- **ESP Flasher Guide:** [ESP_FLASHER_GUIDE.md](ESP_FLASHER_GUIDE.md)
- **Changelog:** [CHANGELOG.md](CHANGELOG.md)

---

## 🎉 Summary

**Before automation:**
1. Manually enable USB Ethernet on Flipper
2. Manually run internet sharing script
3. Configure IP addresses
4. Set up NAT rules
5. Remember to clean up

**With automation:**
1. Plug in Flipper
2. **Done!** ✨

---

**Enjoy zero-configuration USB Ethernet!** 🐬
