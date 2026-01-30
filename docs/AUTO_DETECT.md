# Flipper Zero Auto-Detection

This document describes how to auto-detect a connected Flipper Zero and retrieve its information.

## Detection Logic

The Flipper Zero uses a USB CDC interface with a specific serial name pattern (starts with `flip_`). On macOS, this typically appears as `/dev/cu.usbmodemflip_XXXXXXXX`.

### Python API

The project provides built-in utilities for detection:

1.  **Resolve Port:** `scripts/flipper/utils/cdc.py` contains `resolve_port(logger, portname="auto")`.
2.  **Storage/CLI Access:** `scripts/flipper/storage.py` contains the `FlipperStorage` class which handles the handshake and CLI communication.

### Quick Detection Script

A dedicated detection script is available at the root:

```bash
python3 detect_flipper.py
```

### Manual One-Liner (Shell)

To quickly find the port name without Python:

```bash
ls /dev/cu.usbmodemflip_*
```

To list with serial numbers using `pyserial`:

```bash
python3 -c "import serial.tools.list_ports as lp; [print(p.device) for p in lp.grep('flip_')]"
```

## Device Information

Once connected, sending the `device_info` command to the Flipper CLI provides detailed hardware and firmware metrics.

```python
from flipper.storage import FlipperStorage
with FlipperStorage(port) as storage:
    storage.send("device_info")
    # Read response...
```
