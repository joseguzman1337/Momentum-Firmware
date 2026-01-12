# MCP Servers Configuration - Momentum Firmware

## Summary

Successfully configured and tested 4 AI MCP (Model Context Protocol) servers for the Momentum Firmware project in Claude Code:

1. **ESP-IDF MCP** (External) - ESP32 development
2. **ESP RainMaker MCP** (External) - IoT cloud control
3. **ESP MCP Local** (Local) - Local ESP utilities
4. **Strawberry/Furi MCP** (Local) - **Flipper Zero Build & Runtime Control** ⭐

**Latest Update (2026-01-12):** Added 6 runtime control tools to Strawberry/Furi MCP, bringing total from 4 to 10 tools. New capabilities include GPIO control, system info, storage monitoring, NFC detection, and generic CLI access.

## What Are These MCP Servers?

### 1. ESP-IDF MCP (esp-idf-mcp)
- **Source**: External - from [horw/esp-mcp](https://github.com/horw/esp-mcp)
- **Location**: `~/.claude-mcp-servers/esp-idf-mcp`
- **Purpose**: ESP-IDF project build, flash, and management tools
- **Capabilities**:
  - Install ESP-IDF dependencies
  - Create ESP-IDF projects
  - Set target chip (esp32, esp32c3, esp32s3, etc.)
  - Build ESP-IDF projects
  - List serial ports
  - Flash firmware to ESP devices
  - Run pytest tests

### 2. ESP RainMaker MCP (esp-rainmaker-mcp)
- **Source**: External - from [espressif/esp-rainmaker-mcp](https://github.com/espressif/esp-rainmaker-mcp)
- **Location**: `~/.claude-mcp-servers/esp-rainmaker-mcp`
- **Purpose**: IoT device control through ESP RainMaker cloud
- **Capabilities**:
  - Device management (list nodes, check status, read parameters)
  - Control commands (change device states like power, brightness, temperature)
  - Schedule management (add, edit, remove schedules)
  - Group management (homes/rooms)

### 3. ESP MCP Local (esp-mcp-local)
- **Source**: Local - in `.ai/mcp/servers/esp_mcp`
- **Location**: `/home/d3c0d3r/x/Momentum-Firmware/.ai/mcp/servers/esp_mcp`
- **Purpose**: Local ESP utilities and tools
- **Note**: This is the "Espressif" MCP referenced by the user

### 4. Strawberry/Furi MCP (strawberry-furi-mcp) ⭐ UPDATED
- **Source**: Local - in `.ai/mcp/servers/strawberry_mcp`
- **Location**: `/home/d3c0d3r/x/Momentum-Firmware/.ai/mcp/servers/strawberry_mcp`
- **Purpose**: Flipper Zero firmware build, flash, and **runtime control** tools (FuriOS utilities)
- **Build Capabilities** (Original):
  - Build Flipper Zero firmware using fbt
  - Flash firmware via USB
  - Clean build artifacts
  - WiFi DevBoard configuration
- **Runtime Control Capabilities** (NEW - 2026-01-12):
  - **GPIO Control**: Set/read GPIO pin states (pins 0-13)
  - **System Info**: Get device and firmware information
  - **Storage Info**: Check SD card storage status
  - **NFC Detection**: Detect and read NFC tags
  - **Generic CLI**: Execute arbitrary Flipper CLI commands
- **Total Tools**: 10 (4 build tools + 6 runtime control tools)
- **Note**: "FuriOS" refers to the operating system on Flipper Zero, which is what the user meant by "furios"
- **Documentation**: See `.ai/GETTING_STARTED_RUNTIME_CONTROL.md` for usage examples

## Configuration Details

All MCP servers are configured in Claude's settings at `~/.claude.json` under the Momentum-Firmware project path.

### Claude Configuration Path
```
/home/d3c0d3r/.claude.json
→ projects
  → /home/d3c0d3r/x/Momentum-Firmware
    → mcpServers
```

## Installation Summary

### External MCP Servers
- Cloned to: `~/.claude-mcp-servers/`
- Dependencies installed using `uv` package manager
- Configured with ESP-IDF path: `/home/d3c0d3r/esp/esp-idf`

### Local MCP Servers
- Located in: `.ai/mcp/servers/`
- Dependencies managed via virtual environments
- Integrated with Flipper Zero build tools (fbt)

## Testing

All MCP servers have been tested and verified working using the test script:
```bash
/home/d3c0d3r/x/Momentum-Firmware/.ai/test_mcp_servers.sh
```

Test Results:
- ✅ ESP-IDF MCP: PASSED
- ✅ ESP RainMaker MCP: PASSED
- ✅ ESP MCP Local: PASSED
- ✅ Strawberry/Furi MCP: PASSED

## How to Use

To start using these MCP servers:
1. Restart Claude Code
2. Or start a new conversation in the Momentum-Firmware directory
3. The MCP tools will be available for use

## Example Usage

Ask Claude to:
- "Build the Flipper Zero firmware for target f7"
- "Flash the firmware to the connected Flipper device"
- "List all ESP32 serial ports"
- "Check the status of my ESP RainMaker devices"
- "Create a new ESP-IDF project"

## Clarification on Naming

The user requested 4 MCP servers: "esp, furios, espressif, and strawberry"

**What they actually are:**
1. **esp** → ESP-IDF MCP (External)
2. **furios** → Strawberry/Furi MCP (FuriOS utilities for Flipper Zero)
3. **espressif** → ESP MCP Local (Local ESP utilities)
4. **strawberry** → Strawberry/Furi MCP (Same as #2, has both names)

**Note**: Strawberry/Furi MCP serves both the "furios" and "strawberry" requirements as it provides FuriOS utilities through the Strawberry MCP framework.

## Additional Resources

- [ESP-IDF MCP Documentation](https://github.com/horw/esp-mcp)
- [ESP RainMaker MCP Documentation](https://github.com/espressif/esp-rainmaker-mcp)
- [Espressif Developer Portal](https://developer.espressif.com/blog/2025/07/esp-rainmaker-mcp-server/)
- [Model Context Protocol Docs](https://modelcontextprotocol.io/)

## Date Configured
2026-01-12
