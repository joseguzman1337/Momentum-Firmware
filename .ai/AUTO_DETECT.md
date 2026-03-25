# AI Context: Flipper Auto-Detection

## Shortcuts
- Detection Script: `detect_flipper.py`
- Core Logic: `scripts/flipper/utils/cdc.py` -> `resolve_port()`
- CLI Interaction: `scripts/flipper/storage.py` -> `FlipperStorage`

## Strategy for Gemini CLI
1. Always check for `/dev/cu.usbmodemflip_*` on macOS.
2. Use `scripts/flipper/utils/cdc.py` to resolve the port programmatically.
3. Use `device_info` command via serial to verify device state.

## Current Detected Device
- **Name:** Asch1rp
- **Port:** `/dev/cu.usbmodemflip_Asch1rp1`
- **Firmware:** Momentum (mntm-012)
