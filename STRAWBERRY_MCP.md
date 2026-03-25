# Strawberry MCP

Strawberry MCP is a Furi OS MCP server designed to facilitate Flipper Zero firmware operations and WiFi Devboard deployments. It is based on the [ESP MCP](../esp_mcp/README.md) architecture.

## Features

- **Build Firmware**: Compiles the Flipper Zero firmware using `fbt`.
- **Flash Firmware**: Flashes the firmware to the Flipper Zero via USB.
- **Clean Firmware**: Cleans build artifacts.
- **Deploy WiFi Devboard Config**: Applies mandatory configuration to enforce SD card usage for WiFi Devboard V1 operations.

## WiFi Devboard V1 Configuration

The firmware has been configured to **always use the Flipper Zero SD card** for all WiFi Devboard V1 operations (specifically Marauder).

- **PCAP Saving**: Forced to ON.
- **Log Saving**: Forced to ON.
- **Prompt**: Disabled. The user is no longer asked whether to save to SD card; it is mandatory.

## Usage

You can use the Strawberry MCP tools via your MCP-compliant client.

### Tools

- `build_firmware(target="f7", app_id=None)`: Builds the firmware.
- `flash_firmware()`: Flashes the firmware.
- `clean_firmware()`: Cleans the build.
- `deploy_wifi_devboard_config()`: Confirms the deployment of the WiFi Devboard configuration.

## Setup

The server is registered in `.ai/mcp/codex_server.json` as `strawberry_mcp`.

```json
"strawberry_mcp": {
    "command": "python3",
    "args": [
        "main.py"
    ],
    "cwd": ".ai/mcp/servers/strawberry_mcp",
    "trust": true,
    "description": "Furi OS MCP server for Flipper Zero firmware operations (build, flash, clean) and WiFi Devboard deployment."
}
```
