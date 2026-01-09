# Momentum Firmware - Gemini AI Context

## Project Overview
Momentum Firmware is a feature-rich custom firmware for Flipper Zero, based on the Official Firmware and including features from Unleashed. It's built with a focus on stability, customization, and innovation.

## Technology Stack
- **Primary Languages**: C, C++, Python, JavaScript
- **Build System**: SCons, Make
- **Hardware**: Flipper Zero (STM32WB microcontroller)
- **Key Components**:
  - DriverKit (macOS drivers)
  - NFC protocols and parsers
  - SubGHz radio communication
  - JavaScript runtime for apps
  - BadUSB/BadKB functionality

## Code Style Guidelines

### C/C++ Code
- Follow the existing codebase style
- Use `furi_check()` for null pointer validation
- Memory safety is critical - always validate pointers
- Use `furi_hal_*` APIs for hardware abstraction
- Prefer static analysis-friendly patterns

### Python Code
- PEP 8 compliant
- Use type hints where applicable
- Document complex functions

### JavaScript Code
- ES6+ syntax
- Follow the existing JS API patterns in `applications/system/js_app/`

## Security Requirements
- **Memory Safety**: Always validate pointers, check bounds
- **Input Validation**: Sanitize all user inputs and file paths
- **Path Traversal**: Prevent directory traversal in file operations
- **Cryptography**: Use strong keys (256-bit minimum for ECC)
- **Code Scanning**: Address all CodeQL alerts promptly

## Testing Guidelines
- Test on actual hardware when possible
- Validate SubGHz frequencies within legal limits
- Ensure NFC protocol compliance
- Test power management features thoroughly

## Issue Resolution Workflow
When fixing issues:
1. Analyze the root cause thoroughly
2. Implement the fix with proper error handling
3. Add comments explaining non-obvious logic
4. Include "Closes #N" in commit messages
5. Ensure backward compatibility

## Build Instructions
```bash
# Flash to Flipper via USB
./fbt flash_usb_full

# Build update package
./fbt updater_package

# Launch specific app
./fbt launch APPSRC=app_id
```

## Important Directories
- `applications/` - User-facing applications
- `lib/` - Core libraries and protocols
- `drivers/` - Hardware drivers (including DriverKit)
- `targets/f7/` - Flipper Zero hardware-specific code
- `scripts/` - Build and deployment scripts

## Automation Context
This project uses multiple AI agents:
- **Codex**: Feature implementation and bug fixes
- **Claude**: Security vulnerability remediation
- **Jules**: Asynchronous cloud-based coding tasks
- **Warp**: Code quality analysis
- **Gemini**: Advanced problem-solving and architecture decisions

## Current Priorities
1. Fix remaining open GitHub issues
2. Improve code quality and test coverage
3. Enhance security (address scanning alerts)
4. Optimize performance (SubGHz, NFC processing)
5. Expand JavaScript API capabilities
