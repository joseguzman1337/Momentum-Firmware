# Momentum Firmware - Technology Stack

## Programming Languages

### Primary Languages
- **C** - Core firmware, drivers, and system services (90% of codebase)
- **C++** - Some application components and external libraries
- **Python** - Build system, automation scripts, and AI agents
- **JavaScript** - User applications via MJS runtime engine

### Specialized Languages
- **Assembly** - Low-level hardware initialization and critical paths
- **Shell/Bash** - Build automation and deployment scripts
- **YAML/JSON** - Configuration files and CI/CD workflows

## Core Technologies

### Real-Time Operating System
- **FreeRTOS** - Primary RTOS kernel
- **Furi** - Custom abstraction layer over FreeRTOS
- **Threading Model** - Cooperative multitasking with message queues
- **Memory Management** - Custom heap implementation with debugging

### Hardware Platform
- **STM32WB55** - Dual-core ARM Cortex-M4 + Cortex-M0+ MCU
- **Bluetooth LE** - STM32WB wireless stack
- **Sub-GHz Radio** - CC1101 transceiver for 315/433/868/915 MHz
- **NFC** - ST25R3916 controller for 13.56 MHz operations

### Build System
- **SCons** - Primary build system (Python-based)
- **GCC ARM** - Cross-compilation toolchain
- **Custom FBT** - Flipper Build Tool for application packaging
- **Docker** - Containerized build environments

## Development Dependencies

### Core Libraries
- **mlib** - Memory-efficient C containers and algorithms
- **nanopb** - Protocol Buffers implementation for embedded systems
- **mbedTLS** - Cryptographic library for security functions
- **FatFS** - FAT file system implementation
- **u8g2** - Graphics library for monochrome displays

### Protocol Libraries
- **Digital Signal Processing** - Custom RF signal analysis
- **Infrared** - IR protocol encoding/decoding
- **NFC/RFID** - Multiple protocol implementations
- **SubGhz** - Sub-gigahertz protocol suite
- **OneWire/iButton** - Dallas semiconductor protocols

### JavaScript Runtime
- **MJS** - Minimal JavaScript engine for embedded systems
- **Custom APIs** - Flipper-specific JavaScript bindings
- **Module System** - Dynamic loading of JS applications

## AI Development Stack

### AI Agents & Integration
- **OpenAI Codex** - Code generation and issue resolution
- **Anthropic Claude** - Security analysis and code review
- **Google Gemini** - Architectural decisions and complex refactoring
- **DeepSeek** - Performance optimization and mathematical reasoning
- **Amazon Q** - AWS/cloud infrastructure automation

### AI Coordination Technologies
- **Model Context Protocol (MCP)** - Inter-agent communication
- **RAG System** - Retrieval Augmented Generation for knowledge sharing
- **GitHub API** - Automated issue processing and PR management
- **Docker Containers** - Isolated AI agent execution environments

## Development Commands

### Build Commands
```bash
# Full firmware build and flash
./fbt flash_usb_full

# Build updater package
./fbt updater_package

# Build and launch specific app
./fbt launch APPSRC=app_name

# Build external applications
./fbt fap_dist

# Clean build artifacts
./fbt -c
```

### Development Tools
```bash
# Start debugging session
./fbt debug

# Run unit tests
./fbt test

# Generate documentation
./fbt doxygen

# Lint code
./fbt lint

# Format code
./fbt format
```

### AI Agent Commands
```bash
# Setup MCP integration
./scripts/mcp-setup.sh

# Validate MCP configuration
./scripts/validate-mcp.py

# Start AI orchestrator
python .ai/orchestrator.py --yolo-mode

# Monitor agent logs
tail -f logs/*/$(date +%Y%m%d).log
```

## Version Requirements

### Toolchain Versions
- **GCC ARM** - 10.3.1 or later
- **Python** - 3.8+ for build system, 3.11+ for AI agents
- **SCons** - 4.0+ for build system
- **Git** - 2.30+ with submodule support

### Hardware Requirements
- **Flipper Zero** - Hardware revision 7 or later
- **USB Cable** - For flashing and debugging
- **SD Card** - Class 10, 32GB+ recommended for external apps

### Development Environment
- **Operating Systems** - Linux, macOS, Windows (WSL2)
- **RAM** - 8GB+ recommended for full builds
- **Storage** - 10GB+ for complete toolchain and source
- **Network** - Required for AI agent coordination

## Configuration Files

### Build Configuration
- **`fbt_options.py`** - Build targets and feature flags
- **`SConstruct`** - Main SCons build configuration
- **`target.json`** - Hardware-specific settings

### AI Configuration
- **`.codex/config.toml`** - Codex agent settings
- **`.claude/project.json`** - Claude project configuration
- **`.gemini/settings.json`** - Gemini agent parameters
- **`.ai/*/mcp_server.json`** - MCP server configurations

### IDE Integration
- **`.clangd`** - Language server configuration
- **`.clang-format`** - Code formatting rules
- **`.editorconfig`** - Editor-agnostic formatting

## External Dependencies

### Git Submodules
- **FreeRTOS-Kernel** - RTOS implementation
- **STM32 HAL/CMSIS** - Hardware abstraction layers
- **mbedTLS** - Cryptographic functions
- **nanopb** - Protocol buffer implementation
- **External applications** - Community app repository

### Package Dependencies
- **Python packages** - Listed in `requirements.txt`
- **System packages** - Build tools, debuggers, flashers
- **Docker images** - For containerized builds and AI agents

## Performance Characteristics

### Memory Usage
- **Flash** - ~1MB firmware, ~1MB available for apps
- **RAM** - ~256KB total, ~128KB available for applications
- **Stack** - 4KB per thread typical
- **Heap** - Dynamic allocation with leak detection

### Timing Requirements
- **Real-time** - Sub-millisecond response for RF protocols
- **UI Responsiveness** - 60 FPS display updates
- **Power Management** - Sleep/wake cycles under 100ms
- **Boot Time** - Under 3 seconds from power-on