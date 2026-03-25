# Getting Started: Flipper Zero Runtime Control via AI

## Overview

You can now control your Flipper Zero in real-time using natural language commands through Claude Code! This guide will help you get started with the new runtime control features.

## Prerequisites

### Hardware
- **Flipper Zero** device
- **USB cable** (data-capable, not charge-only)
- Computer with Momentum Firmware repository

### Software
- Claude Code CLI
- Strawberry/Furi MCP server (already configured)
- Flipper Zero connected via USB

## Quick Start

### 1. Connect Your Flipper Zero

```bash
# Connect Flipper Zero via USB

# Verify connection (optional)
./fbt cli
# You should see the Flipper CLI prompt
# Press Ctrl+C to exit
```

### 2. Test Basic GPIO Control

Once connected, you can start using natural language commands:

```
👤 You: "Set GPIO pin 5 to HIGH"

🤖 Claude: I'll set GPIO pin 5 to HIGH state.
   [Calls gpio_set(pin=5, state=True)]
   ✅ GPIO pin 5 set to HIGH
```

### 3. Read GPIO State

```
👤 You: "Read the state of GPIO pin 5"

🤖 Claude: I'll read GPIO pin 5 state.
   [Calls gpio_read(pin=5)]
   Result: {
     "pin": 5,
     "state": "HIGH",
     "success": true
   }
```

### 4. Check Device Information

```
👤 You: "Show me the Flipper system information"

🤖 Claude: I'll get the system information.
   [Calls system_info()]
   ✅ Device info retrieved
```

## Available Commands

### GPIO Control

| Command | Description | Pin Range |
|---------|-------------|-----------|
| `gpio_set(pin, state)` | Set pin HIGH/LOW | 0-13 |
| `gpio_read(pin)` | Read pin state | 0-13 |

**Natural Language Examples:**
- "Set GPIO pin 7 to HIGH"
- "Turn off pin 3"
- "Enable GPIO 5"
- "Check pin 7 state"
- "Is pin 5 high or low?"

### System & Storage

| Command | Description |
|---------|-------------|
| `system_info()` | Get device/firmware info |
| `storage_info()` | Get SD card storage info |

**Natural Language Examples:**
- "Show me device information"
- "What firmware version is running?"
- "Check SD card storage"
- "How much free space on the SD card?"

### NFC Detection

| Command | Description |
|---------|-------------|
| `nfc_detect()` | Detect NFC tag |

**Natural Language Examples:**
- "Detect NFC tag"
- "Is there an NFC card nearby?"
- "Scan for NFC"

### Generic CLI

| Command | Description |
|---------|-------------|
| `flipper_cli(command)` | Execute any CLI command |

**Natural Language Examples:**
- "Execute CLI command 'gpio mode 5 output'"
- "Run 'led r 128' command"
- "Send CLI command 'storage list'"

## Example Workflows

### Example 1: GPIO Testing

Test a GPIO pin end-to-end:

```
👤 "Set GPIO pin 7 to HIGH, then read it back to verify"

🤖 I'll set the pin and verify:
   1. gpio_set(pin=7, state=True)
      ✅ GPIO pin 7 set to HIGH

   2. gpio_read(pin=7)
      ✅ Verified: Pin 7 is HIGH
```

### Example 2: Device Health Check

Check device status:

```
👤 "Check the Flipper system info and storage info"

🤖 I'll check both:
   1. system_info()
      ✅ Firmware: Momentum vX.Y.Z
      ✅ Hardware: Flipper Zero f7

   2. storage_info()
      ✅ Total: 32GB
      ✅ Free: 28GB (87%)
```

### Example 3: NFC Scanning

Detect an NFC tag:

```
👤 "Scan for NFC tags and show me the UID"

🤖 I'll scan for NFC tags:
   nfc_detect()
   ✅ Tag detected!
   UID: 04:A2:B3:C4:D5:E6:F7
```

### Example 4: LED Control via CLI

Control Flipper LED:

```
👤 "Set the red LED to 128 brightness"

🤖 I'll set the LED brightness:
   flipper_cli(command="led r 128")
   ✅ Command executed successfully
```

## GPIO Pin Reference

### Available GPIO Pins (0-13)

Flipper Zero GPIO pins you can control:

- **Pin 0-7**: General purpose I/O
- **Pin 8-13**: Additional GPIO with special functions

**Important:** Check your Flipper Zero pinout diagram to avoid conflicts with connected peripherals.

### GPIO Pin States

- **HIGH (1)**: ~3.3V output
- **LOW (0)**: 0V output

**Input Validation:** The tools automatically validate pin numbers are in the 0-13 range.

## Safety & Best Practices

### Safety First

1. **Check Pin Configuration:** Ensure pins are configured as outputs before setting state
2. **Avoid Short Circuits:** Don't connect GPIO directly to ground when HIGH
3. **Current Limits:** GPIO pins have current limitations, use appropriate resistors
4. **USB Connection:** Keep Flipper connected via USB during operations

### Best Practices

1. **Start Simple:** Test with a single GPIO pin first
2. **Verify State:** Always read back GPIO state after setting
3. **Use Natural Language:** Describe what you want, let AI handle the commands
4. **Check Logs:** Review `.ai/logs/strawberry_mcp/` for detailed operation logs

### Error Handling

The tools include built-in error handling:

```python
# Invalid pin number
👤 "Set GPIO pin 20 to HIGH"
🤖 Error: Invalid pin number 20. Must be 0-13.

# Device not connected
👤 "Read GPIO pin 5"
🤖 Error: Could not connect to Flipper device
    Please ensure it's connected via USB
```

## Troubleshooting

### Problem: "Could not connect to device"

**Solution:**
1. Verify Flipper is connected via USB
2. Check USB cable is data-capable (not charge-only)
3. Try: `./fbt cli` to test connection manually
4. Ensure no other programs are using the serial port

### Problem: "GPIO command failed"

**Solution:**
1. Check pin number is in valid range (0-13)
2. Verify pin isn't reserved by active application
3. Ensure Flipper isn't in deep sleep mode
4. Try rebooting Flipper and reconnecting

### Problem: "NFC detection not working"

**Solution:**
1. Ensure NFC card is close to Flipper (~3-5cm)
2. Check NFC card is supported type (ISO 14443A/B, etc.)
3. Try: `./fbt cli -c 'nfc detect'` manually
4. Verify NFC module isn't disabled in settings

### Problem: "Commands are slow"

**Expected Behavior:**
- CLI-based commands have higher latency (~1-2 seconds)
- This is normal for the current implementation
- Future updates will use direct RPC for faster response

## Advanced Usage

### Combining Multiple Operations

```
👤 "Set pins 5, 6, and 7 to HIGH, then verify all three"

🤖 I'll set all three pins and verify:
   1. gpio_set(pin=5, state=True) ✅
   2. gpio_set(pin=6, state=True) ✅
   3. gpio_set(pin=7, state=True) ✅

   Verification:
   4. gpio_read(pin=5) → HIGH ✅
   5. gpio_read(pin=6) → HIGH ✅
   6. gpio_read(pin=7) → HIGH ✅

   All pins set successfully!
```

### Using CLI for Advanced Features

```
👤 "Configure pin 5 as output with pull-up"

🤖 I'll configure the pin:
   flipper_cli(command="gpio mode 5 output_pp")
   ✅ Pin 5 configured as push-pull output
```

### Integration with Build Workflow

```
👤 "Build the firmware, flash it, and then test GPIO pin 5"

🤖 Complete workflow:
   1. clean_firmware() ✅
   2. build_firmware(target="f7") ✅
   3. flash_firmware() ✅
   4. [Wait for reboot]
   5. gpio_set(pin=5, state=True) ✅
   6. gpio_read(pin=5) → HIGH ✅

   Firmware deployed and GPIO tested!
```

## Command Reference Card

### Quick Command List

```bash
# GPIO
"Set GPIO pin X to HIGH/LOW"
"Read GPIO pin X"

# System
"Show device info"
"Check storage info"

# NFC
"Detect NFC tag"
"Scan for NFC"

# CLI
"Execute CLI command 'COMMAND'"
"Run 'COMMAND' on Flipper"

# Build (existing)
"Build firmware"
"Flash firmware"
"Clean build"
```

## Logs & Debugging

All operations are logged to:

```
.ai/logs/strawberry_mcp/
├── mcp-build.log          # Build operations
├── mcp-flash.log          # Flash operations
├── mcp-clean.log          # Clean operations
└── [timestamped logs]     # Historical logs
```

View recent operations:
```bash
# View latest log
tail -50 .ai/logs/strawberry_mcp/mcp-build-live.log

# Search for errors
grep -i error .ai/logs/strawberry_mcp/*.log
```

## What's Next?

### Coming Soon
- **SubGHz control** - RF transmission and reception
- **IR control** - Infrared send/receive
- **RFID tools** - RFID card read/write/emulation
- **LED control** - RGB LED pattern control
- **Vibration control** - Haptic feedback control

### Future Enhancements
- **Direct RPC** - Faster communication via Protobuf RPC
- **Wi-Fi Control** - Wireless control via ESP32-S2 DevBoard
- **Rust MCP Service** - Native firmware service for best performance
- **Tool Discovery** - Automatic feature detection

## Getting Help

### Resources
- **Quick Reference:** `.ai/FURI_MCP_QUICK_REFERENCE.md`
- **Architecture:** `.ai/FURI_CORE_OS_MCP.md`
- **Roadmap:** `.ai/docs/MCP_IMPLEMENTATION_ROADMAP.md`
- **Changelog:** `.ai/CHANGELOG_MCP.md`

### Community
- GitHub Issues: Report bugs and request features
- Discussions: Ask questions and share examples

## Summary

You now have 10 MCP tools for controlling Flipper Zero:

**Build Tools (4):**
- build_firmware
- flash_firmware
- clean_firmware
- deploy_wifi_devboard_config

**Runtime Control (6):**
- gpio_set
- gpio_read
- system_info
- storage_info
- nfc_detect
- flipper_cli

**All accessible via natural language through Claude Code!**

Start with simple GPIO commands and gradually explore more features. Have fun controlling your Flipper Zero with AI! 🚀

---

**Last Updated:** 2026-01-12
**Version:** 1.0 (Week 1 MVP)
**Implementation Status:** Option A (CLI-based tools)
