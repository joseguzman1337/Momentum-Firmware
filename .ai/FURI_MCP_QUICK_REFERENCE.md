# Furi Core OS MCP - Quick Reference Guide

## Overview

This guide provides quick examples of using the Furi Core OS AI MCP tools for Flipper Zero development through natural language commands.

## Available MCP Servers

1. **esp-idf-mcp** - ESP32 development tools
2. **esp-rainmaker-mcp** - IoT device control
3. **esp-mcp-local** - Local ESP utilities
4. **strawberry-furi-mcp** - **Furi OS / Flipper Zero tools** ⭐

## Furi MCP Tools

### 1. Build Firmware

```python
build_firmware(target: str = "f7", app_id: str = None)
```

**Examples:**

```
👤 "Build the firmware for Flipper Zero"
🤖 Executing: build_firmware(target="f7")

👤 "Build the SubGHz application only"
🤖 Executing: build_firmware(target="f7", app_id="applications/main/subghz")

👤 "Build for f18 hardware target"
🤖 Executing: build_firmware(target="f18")
```

**What it does:**
- Runs `./fbt` with appropriate build commands
- Streams build output in real-time
- Saves logs to `.ai/logs/strawberry_mcp/`
- Returns build status and timing info

### 2. Flash Firmware

```python
flash_firmware()
```

**Examples:**

```
👤 "Flash the firmware to my Flipper"
🤖 Executing: flash_firmware()

👤 "Upload the firmware via USB"
🤖 Executing: flash_firmware()
```

**What it does:**
- Runs `./fbt flash_usb_full`
- Flashes firmware to connected Flipper Zero
- Provides real-time status updates
- Returns flash completion status

### 3. Clean Build

```python
clean_firmware()
```

**Examples:**

```
👤 "Clean the build artifacts"
🤖 Executing: clean_firmware()

👤 "Start fresh, remove all build files"
🤖 Executing: clean_firmware()
```

**What it does:**
- Runs `./fbt -c`
- Removes all compiled objects and binaries
- Prepares for clean rebuild

### 4. Configure WiFi DevBoard

```python
deploy_wifi_devboard_config()
```

**Examples:**

```
👤 "Apply WiFi DevBoard configuration"
🤖 Executing: deploy_wifi_devboard_config()

👤 "Set up WiFi DevBoard to use SD card"
🤖 Executing: deploy_wifi_devboard_config()
```

**What it does:**
- Configures Flipper to use SD card for WiFi DevBoard
- Applies mandatory WiFi DevBoard V1 settings

### 5. GPIO Control - Set Pin State

```python
gpio_set(pin: int, state: bool)
```

**Examples:**

```
👤 "Set GPIO pin 5 to HIGH"
🤖 Executing: gpio_set(pin=5, state=True)
   ✅ GPIO pin 5 set to HIGH

👤 "Turn off pin 3"
🤖 Executing: gpio_set(pin=3, state=False)
   ✅ GPIO pin 3 set to LOW

👤 "Enable GPIO 7"
🤖 Executing: gpio_set(pin=7, state=True)
```

**What it does:**
- Sets GPIO pin state (HIGH/LOW) on Flipper Zero
- Pin numbers: 0-13
- Uses `fbt cli` for device communication
- Requires Flipper connected via USB

### 6. GPIO Control - Read Pin State

```python
gpio_read(pin: int)
```

**Examples:**

```
👤 "Read the state of GPIO pin 5"
🤖 Executing: gpio_read(pin=5)
   {
     "pin": 5,
     "state": "HIGH",
     "raw_output": "Pin 5: HIGH",
     "success": true
   }

👤 "Check if pin 3 is high or low"
🤖 Executing: gpio_read(pin=3)
   {
     "pin": 3,
     "state": "LOW",
     "success": true
   }
```

**What it does:**
- Reads current GPIO pin state from Flipper Zero
- Returns pin state (HIGH/LOW) and raw output
- Pin numbers: 0-13
- Requires Flipper connected via USB

### 7. System Information

```python
system_info()
```

**Examples:**

```
👤 "Get Flipper device information"
🤖 Executing: system_info()
   {
     "success": true,
     "device_info": "Flipper Zero f7...",
     "raw_output": "..."
   }

👤 "Show me the firmware version"
🤖 Executing: system_info()
```

**What it does:**
- Retrieves Flipper Zero system information
- Shows firmware version, hardware info
- Uses `device_info` CLI command
- Requires Flipper connected via USB

### 8. Storage Information

```python
storage_info()
```

**Examples:**

```
👤 "Check SD card storage"
🤖 Executing: storage_info()
   {
     "success": true,
     "storage_info": "Total: 32GB, Free: 28GB",
     "raw_output": "..."
   }

👤 "How much free space on the SD card?"
🤖 Executing: storage_info()
```

**What it does:**
- Gets SD card storage information
- Shows total size and free space
- Uses `storage info` CLI command
- Requires Flipper connected via USB

### 9. NFC Tag Detection

```python
nfc_detect()
```

**Examples:**

```
👤 "Detect NFC tag"
🤖 Executing: nfc_detect()
   {
     "success": true,
     "tag_detected": true,
     "nfc_output": "UID: 04:A2:B3:C4...",
     "raw_output": "..."
   }

👤 "Is there an NFC card nearby?"
🤖 Executing: nfc_detect()
   {
     "success": true,
     "tag_detected": false
   }
```

**What it does:**
- Detects NFC tags using Flipper's NFC module
- Returns detection status and UID if found
- Uses `nfc detect` CLI command
- Requires Flipper connected via USB

### 10. Generic CLI Command

```python
flipper_cli(command: str)
```

**Examples:**

```
👤 "Execute CLI command 'gpio mode 5 output'"
🤖 Executing: flipper_cli(command="gpio mode 5 output")
   {
     "success": true,
     "stdout": "Pin 5 mode set to output",
     "stderr": "",
     "return_code": 0
   }

👤 "Run 'led r 128' command"
🤖 Executing: flipper_cli(command="led r 128")
```

**What it does:**
- Executes arbitrary Flipper CLI commands
- Provides full CLI feature access
- Sanitizes input to prevent command injection
- Returns stdout, stderr, and return code
- Requires Flipper connected via USB

## Common Workflows

### Full Build and Flash Workflow

```
👤 "Build and flash the firmware"

🤖 I'll build the firmware and then flash it to your Flipper:

1. build_firmware(target="f7")
   ✅ Build completed in 45.2 seconds

2. flash_firmware()
   ✅ Flash completed in 12.5 seconds

Done! Firmware is now running on your Flipper Zero.
```

### Debug Build Errors

```
👤 "The build is failing, can you try a clean build?"

🤖 I'll clean the build directory and rebuild:

1. clean_firmware()
   ✅ Build artifacts cleaned

2. build_firmware(target="f7")
   ✅ Build completed successfully!

The clean build resolved the issue.
```

### Build Specific Application

```
👤 "I only need to build the NFC application"

🤖 build_firmware(target="f7", app_id="applications/main/nfc")
   ✅ NFC application built successfully

The FAP file is in: build/f7/applications/main/nfc/
```

## Furi OS Context for AI

When working with the Furi MCP, Claude has access to:

### Build Logs
```
.ai/logs/strawberry_mcp/
├── mcp-build.log              # Latest build output
├── mcp-build-20260112-115530.log  # Timestamped builds
├── mcp-flash.log              # Latest flash output
└── mcp-build-live.log         # Real-time streaming
```

### Furi Core API Knowledge
- Thread management (`furi_thread_*`)
- Event loops (`furi_event_loop_*`)
- Memory management (`furi_alloc`, `furi_free`)
- Service registry (`furi_record_*`)
- Safety checks (`furi_check`, `furi_assert`)

### Hardware Targets
- **f7** - Flipper Zero (primary target)
- **f18** - Future hardware variants

## Natural Language Examples

### Simple Commands

```
"Build the firmware"
"Flash to Flipper"
"Clean the build"
"Build SubGHz app"
"Set GPIO pin 5 to HIGH"
"Read GPIO pin 3"
"Check storage info"
"Detect NFC tag"
```

### Complex Commands

```
"Build the firmware for f7, and if it succeeds, flash it to the device"

"Clean the build, rebuild from scratch, and show me any warnings"

"Build the NFC reader application and check the build logs for errors"

"Flash the latest firmware and tell me if it completed successfully"

"Set GPIO pin 7 to HIGH and then read its state to verify"

"Check system info and storage info to see device status"

"Try to detect an NFC tag and show me the UID if found"
```

### Debugging Workflows

```
"The firmware is crashing on boot. Can you rebuild with debug symbols?"

"I need to check the build output for compilation warnings"

"Show me the last flash log to see if there were any errors"

"Build the firmware and save the output so I can review the memory usage"
```

## Understanding Build Output

### Successful Build
```
[Build completed in 42.31 seconds]

Return code: 0
Status: ✅ Success
Artifacts: build/f7/firmware.bin
```

### Build Errors
```
[Build failed]

Return code: 2
Status: ❌ Failed
Error: Compilation error in applications/main/nfc/nfc_app.c:123
```

### Flash Status
```
[Flash completed in 8.74 seconds]

Status: ✅ Success
Device: Flipper Zero connected via USB
```

## Advanced Usage

### Environment Variables

The MCP server runs with:
```
PYTHONPATH=/path/to/.ai/mcp/servers/strawberry_mcp
```

### Working Directory

All commands execute from:
```
/home/d3c0d3r/x/Momentum-Firmware
```

### Log Retention

Logs are kept with timestamps for debugging:
- Latest logs are overwritten: `mcp-build.log`
- Historical logs are preserved: `mcp-build-20260112-*.log`

## Integration with Other Tools

### Combine with ESP MCPs

```
👤 "Build the Flipper firmware and also build my ESP32 project"

🤖 I'll build both:

1. build_firmware(target="f7")  # Furi MCP
   ✅ Flipper firmware built

2. build_esp_project(path="/path/to/esp32")  # ESP MCP
   ✅ ESP32 project built

Both builds completed successfully!
```

### Automated Testing

```
👤 "Build the firmware, flash it, and monitor for crashes"

🤖 Complete workflow:

1. clean_firmware()
2. build_firmware(target="f7")
3. flash_firmware()
4. [Monitor serial output for furi_check crashes]

Ready for testing!
```

## Tips & Tricks

### 🔹 Use Descriptive Commands
```
❌ "build"
✅ "Build the firmware for Flipper Zero"
```

### 🔹 Check Logs on Errors
```
👤 "Build failed, can you show me the error?"
🤖 [Reads mcp-build.log and explains the error]
```

### 🔹 Iterative Development
```
1. "Build the NFC app"
2. "Flash it to test"
3. [Make changes]
4. "Rebuild just the NFC app"
5. "Flash the update"
```

### 🔹 Combine Multiple Operations
```
👤 "Clean, build, and flash in one go"
🤖 Executing sequence:
   1. clean_firmware()
   2. build_firmware()
   3. flash_firmware()
```

## Troubleshooting

### Build Hangs
```
👤 "The build seems stuck"
🤖 Let me check the live log:
   [Reads mcp-build-live.log]
   "It's currently compiling furi_hal_usb.c, should complete soon"
```

### Flash Fails
```
👤 "Flash isn't working"
🤖 Common issues:
   - Flipper not connected via USB
   - USB cable is data-only
   - Device in DFU mode (need to exit)
   - Permissions issue with /dev/ttyACM*
```

### Wrong Target
```
👤 "I built for f18 but need f7"
🤖 No problem:
   clean_firmware()
   build_firmware(target="f7")
```

## Summary

The Furi Core OS MCP integration provides natural language access to Flipper Zero development and runtime control:

**Build Tools:**
- ✅ Build firmware with AI commands
- ✅ Flash to device automatically
- ✅ Monitor builds in real-time
- ✅ Access detailed logs and diagnostics
- ✅ Iterate quickly with clean/rebuild cycles

**Runtime Control:**
- ✅ GPIO control (read/write pins)
- ✅ System information queries
- ✅ Storage/SD card monitoring
- ✅ NFC tag detection
- ✅ Generic CLI command execution

**Integration:**
- ✅ Works with ESP32 development tools
- ✅ Natural language interface via Claude Code
- ✅ Real-time device interaction
- ✅ Secure command sanitization

**Total: 10 MCP tools** for comprehensive Flipper Zero control!

---

**Note**: "FuriOS" = Furi Operating System, the custom RTOS for Flipper Zero built on FreeRTOS.
