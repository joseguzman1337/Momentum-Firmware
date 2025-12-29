# Momentum Firmware - Gemini AI Context

## Project Overview
Momentum Firmware is a feature-rich custom firmware for Flipper Zero, based on the Official Firmware and including features from Unleashed. It's built with a focus on stability, customization, and innovation.

## Technology Stack
- **Primary Languages**: C, C++, Python (tools/scripts), JavaScript (user apps)
- **Build System**: SCons (wrapped by `fbt`)
- **Hardware**: Flipper Zero (STM32WB microcontroller)
- **Key Components**:
  - `Furi`: Core OS primitive and system API
  - `DriverKit`: Hardware abstraction and drivers
  - `Applications`: User-facing functionality
  - `Services`: Background services

## Build & Development (FBT)
The project uses `fbt` (Flipper Build Tool) for all operations.

### Essential Commands
- **Build & Flash (USB)**: `./fbt flash_usb_full`
- **Build & Flash (SWD)**: `./fbt flash` (requires ST-Link/CMSIS-DAP)
- **Build Update Package**: `./fbt updater_package`
- **Launch Single App**: `./fbt launch APPSRC=applications/path/to/app` (Builds and runs app)
- **Format Code**: `./fbt format` (C/C++) or `./fbt format_py` (Python)
- **Lint Code**: `./fbt lint` or `./fbt lint_py`
- **Generate VSCode Config**: `./fbt vscode_dist`

## Code Style Guidelines

### C/C++ (Core Firmware)
- **Naming**:
  - Types/Structs: `PascalCase` (e.g., `FuriHalUsb`)
  - Functions: `snake_case` (e.g., `furi_hal_usb_init`)
  - Files: `snake_case` matching content prefix (e.g., `subghz_keystore.h`)
- **Safety**:
  - Use `furi_check()` for null pointer validation.
  - Always validate pointers and bounds.
  - Use `furi_hal_*` APIs for hardware interaction.
- **Formatting**: 4 spaces indentation. Run `./fbt format` before committing.

### Python (Scripts/Tools)
- Follow PEP 8 standards.
- Use `black` for formatting (via `./fbt format_py`).

### JavaScript (JS Apps)
- ES6+ syntax.
- Follow patterns in `applications/system/js_app/`.

## Directory Structure
- `applications/`: User-facing applications and services.
  - `main/`: Core apps (Main Menu, Passport, etc.).
  - `services/`: System services (Notification, GUI, etc.).
  - `external/`: External plugins/apps.
- `furi/`: Core system kernel and API.
- `lib/`: Shared libraries and protocol parsers.
- `targets/`: Hardware target definitions (mainly `f7` for Flipper Zero).
- `scripts/`: Build scripts and automation tools.
- `.ai/`: AI Agent Ecosystem configuration (Orchestrator, RAG, MCP).

## AI Agent Ecosystem
This project utilizes a multi-agent system for automation:
- **Codex**: Feature implementation and bug fixing.
- **Claude**: Security analysis and vulnerability remediation.
- **Jules**: Asynchronous cloud tasks.
- **Warp**: Code quality and documentation.
- **Gemini**: Architecture and complex problem solving (That's me!).

## Workflow Notes
- **Issue Resolution**: Analyze root cause -> Implement fix -> Add comments -> "Closes #N".
- **Testing**: Test on hardware if possible. Verify SubGHz compliance.
- **Security**: Address CodeQL alerts promptly. Validate all inputs.
