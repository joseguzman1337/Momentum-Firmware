---
name: flipper-zero-dev
description: Auto-detection and interaction with Flipper Zero hardware. Use when the user needs to find a connected Flipper, retrieve device information, or perform serial CLI operations.
---

# Flipper Zero Development Skill

This skill provides specialized knowledge and workflows for interacting with Flipper Zero hardware via USB.

## Auto-Detection Workflow

To find a connected Flipper Zero and retrieve its hardware and firmware details, use the `detect_flipper.py` script.

```bash
python3 scripts/detect_flipper.py
```

## Core APIs and Scripts

### Port Resolution
Implementation: `scripts/flipper/utils/cdc.py:resolve_port(logger, portname="auto")`
Logic: Scans serial ports for the `flip_` prefix.

### CLI and Storage Interaction
Implementation: `scripts/flipper/storage.py` -> `FlipperStorage`
Use this class to send commands and receive data from the device.

## Example Usage

### Getting Device Info
```python
from flipper.storage import FlipperStorage
from flipper.utils.cdc import resolve_port

port = resolve_port(logger)
with FlipperStorage(port) as storage:
    storage.send("device_info\r")
    response = storage.read.until(storage.CLI_PROMPT)
    print(response.decode())
```

### Manual Discovery (Shell)
- **macOS**: `ls /dev/cu.usbmodemflip_*`
- **Linux**: `ls /dev/ttyACM*` (look for Flipper-specific IDs)