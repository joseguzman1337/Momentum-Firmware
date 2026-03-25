# Momentum Firmware - Codex AI Integration Agent

## Overview
Codex AI Integration Agent focuses on feature implementation, bug fixes, and third-party integrations (like Slack).

## Hardware Interaction
- **Auto-Detection**: Use `python3 detect_flipper.py` for quick device discovery and info.
- **Core Logic**: Implementation resides in `scripts/flipper/utils/cdc.py:resolve_port`.
- **CLI Access**: `scripts/flipper/storage.py` provides the `FlipperStorage` class for serial communication.

## Key Directories
- `applications/` - User-facing applications
- `lib/` - Core libraries and protocols
- `scripts/` - Build and deployment scripts
