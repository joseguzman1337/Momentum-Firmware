# WARP.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

## Project Overview

Momentum Firmware is a custom firmware for Flipper Zero based on the Official Firmware, with extensive modifications and enhancements. It's built using the FBT (Flipper Build Tool) system which wraps SCons.

## Common Development Commands

### Building
```bash
# Build firmware (default target)
./fbt

# Build with specific configuration
./fbt COMPACT=1 DEBUG=0

# Build for specific hardware target
./fbt TARGET_HW=7

# Build external apps (FAPs)
./fbt faps

# Build and create update package
./fbt updater_package

# Build for distribution
./fbt fap_dist
```

### Flashing & Debugging
```bash
# Smart USB flash with updater package + AI-style CLI output (recommended)
./fbt smart_flash

# Classic USB flash
./fbt flash_usb_full

# Flash via SWD
./fbt flash

# Debug firmware
./fbt debug

# Debug with Blackmagic probe
./fbt blackmagic

# Open CLI session
./fbt cli
```

### Code Quality
```bash
# Format all code
./fbt format_all

# Lint all code  
./fbt lint_all

# Format only C/C++
./fbt format

# Format only Python
./fbt format_py

# Format images
./fbt format_img
```

### Single App Development
```bash
# Build specific app by ID
./fbt fap_APPID

# Build and launch app
./fbt launch APPSRC=applications_user/path/to/app

# Build app without launching
./fbt build APPSRC=applications_user/path/to/app
```

### Testing
```bash
# Build with unit tests
./fbt FIRMWARE_APP_SET=unit_tests

# Build minimal test configuration
./fbt FIRMWARE_APP_SET=unit_tests_min
```

## Architecture Overview

### Core Components

**FBT (Flipper Build Tool)** - Main build system entry point (`./fbt`) that wraps SCons. Handles toolchain management, cross-compilation for ARM Cortex-M4, and complex dependency management.

**Furi** - The core OS abstraction layer providing:
- RTOS primitives (threads, mutexes, semaphores, event loops)
- Memory management
- Hardware abstraction interfaces

**Applications Structure**:
- `applications/main/` - Core apps (NFC, SubGHz, Infrared, etc.)
- `applications/services/` - Background services (GUI, Storage, Power, etc.) 
- `applications/system/` - Utility apps and pre-packaged externals
- `applications/settings/` - Configuration apps
- `applications/debug/` - Factory testing and debug tools
- `applications_user/` - User-developed external apps

### Application Types (FlipperAppType)
- **SERVICE** - System services loaded at startup
- **APP/MENUEXTERNAL** - Main menu applications
- **EXTERNAL** - Apps built as FAP files for SD card
- **PLUGIN** - Components loaded by other apps
- **SETTINGS** - System settings screens
- **STARTUP** - Boot-time initialization hooks
- **DEBUG** - Development/testing tools

### Build System Details

The build system uses a multi-environment approach:
- **coreenv** - Base ARM cross-compilation environment
- **distenv** - Distribution and flashing environment  
- **firmware_env** - Firmware-specific build environment
- **updater_env** - Self-update package environment (if enabled)

Key build artifacts:
- `.elf` files for debugging
- `.bin` files for flashing
- `.fap` files for external apps (Flipper App Package)
- Update packages (`.fuf` files)

### FAP (External App) Development

External apps are built as position-independent executables with SDK API compatibility:

**Manifest Requirements** (`application.fam`):
```python
App(
    appid="my_app",
    name="My App", 
    apptype=FlipperAppType.EXTERNAL,
    entry_point="my_app_main",
    stack_size=2 * 1024,
    fap_category="Tools",
    fap_version="1.0",
    fap_icon="icon.png"
)
```

**Key Constraints**:
- Must use only exposed SDK APIs from `api_symbols.csv`
- Limited to available RAM (FAPs load into RAM)
- API version compatibility enforced by semantic versioning

### Hardware Targets

Firmware supports multiple hardware configurations via target definitions in `targets/`. Default is TARGET_HW=7 (Flipper Zero). Each target defines:
- Linker scripts
- Hardware abstraction layer
- SDK symbol tables
- Compatible app sets

### Asset System

Momentum firmware includes an enhanced asset system:
- **Asset Packs** - Theme-like bundles of animations, icons, fonts
- **Icons** - PNG assets compiled to C headers
- **Animations** - Frame-based animations with metadata
- **Resources** - SD card content packaged with firmware

## Development Workflow

### Setting Up Development Environment
```bash
# Clone with submodules
git clone --recursive https://github.com/Next-Flip/Momentum-Firmware.git

# Set up VSCode (one time)
./fbt vscode_dist

# Verify build works
./fbt
```

### Creating External Apps
1. Create folder in `applications_user/`
2. Write `application.fam` manifest
3. Implement app with entry point function
4. Build and test: `./fbt launch APPSRC=applications_user/my_app`

### Modifying Core Firmware
1. Modify source in appropriate `applications/` subfolder
2. Update manifest if adding new dependencies
3. Rebuild: `./fbt`
4. Flash: `./fbt flash_usb_full`

## Important Configuration Files

- **`fbt_options.py`** - Main build configuration (optimization, targets, app sets)
- **`SConstruct`** - SCons entry point defining all build targets
- **`firmware.scons`** - Core firmware build logic
- **`site_scons/`** - Custom SCons tools and utilities
- **`CODING_STYLE.md`** - Code formatting and style requirements

## Full Terminal Use

Warp in this repository is configured to support Warp's Full Terminal Use capability, which allows the agent to operate inside interactive terminal applications (database shells, debuggers, REPLs, dev servers, editors, etc.).

See the internal doc for behavior and usage details:
- `.ai/docs/full-terminal-use.md`

When using Full Terminal Use, prefer to:
- Let the agent handle mechanical/iterative commands.
- Take over manually for sensitive operations (credentials, production systems), then hand control back.

For global permission defaults and credit usage, refer to the online Warp docs.

## Debugging & Development Tips

### Memory Profiling
Use CLI commands on device:
- `free` - Show memory usage
- `top` - Show running tasks and stack usage

### API Development
When adding new APIs for external apps:
1. Add function to appropriate header in SDK_HEADERS list
2. Build will fail and prompt to update `api_symbols.csv`
3. Mark new symbols with `+` to expose or `-` to hide
4. API version auto-increments on changes

### Asset Development
Images must be:
- 1-bit depth for icons (black/white)
- Follow naming convention in assets/ReadMe.md
- Use `./fbt format_img` to validate and optimize

## Security & Deployment

Firmware includes multiple security layers:
- Asset pack validation
- FAP signature verification (in official builds)
- Memory protection and stack guards
- Secure boot support (hardware dependent)

For deployment, use update packages created by `./fbt updater_package` rather than direct binary flashing in production.
