# Momentum Firmware - Claude Code Context

## Project Overview
Custom firmware for Flipper Zero based on Official Firmware with enhanced features.

## Build System
- Uses `fbt` (Flipper Build Tool) - Python-based SCons wrapper
- Target: `f7` (Flipper Zero hardware)
- ARM Cortex-M4 architecture

## Key Commands
```bash
# Full firmware build and flash
./fbt flash_usb_full

# Build updater package
./fbt updater_package

# Build single app
./fbt launch APPSRC=app_name

# Run tests
./fbt test

# Format code
./fbt format
```

## Directory Structure
- `applications/` - Apps and services
- `firmware/` - Core firmware code
- `lib/` - Libraries and drivers
- `scripts/` - Build and utility scripts
- `assets/` - Graphics and resources

## Development Notes
- Code style: Follow existing patterns
- Testing: Run `./fbt test` before commits
- Dependencies: ARM toolchain, Python 3.8+, Git submodules
- Build artifacts in `build/` directory

## AI Agent Integration
This project includes automated AI agents for:
- Issue resolution (Codex, Claude, Jules, Gemini, DeepSeek)
- Security scanning and fixes
- Code quality improvements
- Documentation updates

@AmazonQ.md