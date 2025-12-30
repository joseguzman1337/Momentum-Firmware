# Momentum Firmware - Project Structure

## Root Directory Organization

### Core Firmware Components
- **`furi/`** - Core RTOS abstraction layer and system services
- **`lib/`** - Third-party libraries and hardware drivers
- **`targets/`** - Hardware-specific implementations (f7, f18)
- **`applications/`** - Main application suite organized by category

### Application Categories
- **`applications/main/`** - Core user applications (Archive, BadUSB, GPIO, NFC, SubGhz, etc.)
- **`applications/services/`** - System services (GUI, Storage, Bluetooth, Desktop, etc.)
- **`applications/settings/`** - Configuration applications
- **`applications/system/`** - System-level applications (FindMy, HID, JS runtime, Updater)
- **`applications/debug/`** - Development and testing tools
- **`applications/external/`** - Community-contributed applications (200+ apps)

### AI Development Infrastructure
- **`.ai/`** - AI agent automation system
  - **`agents/`** - Core AI automation scripts
  - **`codex/`** - OpenAI Codex integration
  - **`claude/`** - Anthropic Claude security agent
  - **`gemini/`** - Google Gemini super-agent
  - **`deepseek/`** - DeepSeek optimization agent
  - **`amazonq/`** - AWS cloud infrastructure agent
  - **`mcp/`** - Model Context Protocol servers
  - **`rag/`** - Retrieval Augmented Generation system

### Development Tools & Configuration
- **`scripts/`** - Build automation, debugging, and utility scripts
- **`site_scons/`** - SCons build system extensions
- **`toolchain/`** - Cross-compilation toolchain
- **`documentation/`** - Comprehensive project documentation

### Assets & Resources
- **`assets/`** - Icons, animations, fonts, and asset packs
  - **`icons/`** - UI icons organized by category
  - **`dolphin/`** - Flipper mascot animations
  - **`packs/`** - Asset pack templates and examples
- **`logs/`** - AI agent execution logs organized by agent type

### IDE & Editor Integration
- **`.codex/`** - Codex AI integration configuration
- **`.claude/`** - Claude AI project settings
- **`.gemini/`** - Gemini AI commands and policies
- **`.amazonq/`** - Amazon Q rules and memory bank
- **`.cursor/`** - Cursor editor rules

## Architectural Patterns

### Layered Architecture
1. **Hardware Abstraction Layer (HAL)** - `targets/f7/furi_hal/`
2. **Core Services Layer** - `furi/core/` and `applications/services/`
3. **Application Layer** - `applications/main/` and `applications/external/`
4. **User Interface Layer** - GUI services and view management

### Service-Oriented Design
- **Record System** - Service registration and discovery
- **Event-Driven Architecture** - Message queues and pub/sub patterns
- **Worker Threads** - Background processing for protocols and I/O

### Plugin Architecture
- **External Applications** - Dynamically loaded FAP (Flipper Application Package) files
- **Protocol Plugins** - Modular protocol implementations for SubGhz, NFC, etc.
- **Asset Pack System** - Runtime theme and resource loading

### AI Agent Coordination
- **MCP Protocol** - Inter-agent communication via Model Context Protocol
- **Task Routing** - Automatic issue assignment to appropriate AI agents
- **RAG System** - Shared knowledge base for AI coordination
- **YOLO Mode** - Autonomous operation with auto-merge capabilities

## Key Components Relationships

### Core Dependencies
- **Furi** → **FreeRTOS** (RTOS kernel)
- **Applications** → **Furi Services** (system abstraction)
- **HAL** → **STM32 Libraries** (hardware drivers)

### Service Interactions
- **GUI Service** ↔ **Input Service** (user interaction)
- **Storage Service** ↔ **File System** (data persistence)
- **Notification Service** ↔ **Power/Light/Vibro** (user feedback)

### Application Communication
- **Record System** - Service discovery and access
- **Message Queues** - Inter-thread communication
- **Event Loops** - Asynchronous event handling

## Build System Architecture

### SCons-Based Build
- **`SConstruct`** - Main build configuration
- **`fbt_options.py`** - Build options and target configuration
- **`site_scons/`** - Custom build tools and extensions

### Target Configuration
- **Hardware Targets** - f7 (STM32WB55), f18 (future hardware)
- **Build Variants** - Debug, Release, with different feature sets
- **Application Packaging** - FAP generation for external apps

### Asset Processing
- **Icon Compilation** - PNG to C array conversion
- **Animation Processing** - Frame sequence optimization
- **Font Generation** - Custom font format creation

## Development Workflow Integration

### AI-Powered Development
- **Issue Detection** - GitHub API monitoring
- **Automated Fixes** - Multi-agent problem resolution
- **Code Review** - Automated security and quality analysis
- **Documentation** - Auto-generated docs and changelogs

### Quality Assurance
- **Static Analysis** - PVS-Studio integration
- **Unit Testing** - Automated test execution
- **Hardware-in-Loop** - Device testing automation
- **Performance Monitoring** - Memory and timing analysis