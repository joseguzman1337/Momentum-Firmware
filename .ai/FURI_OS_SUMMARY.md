# Furi Core OS - Complete Summary

## What You Asked About: "furi core os of flipper zero ai mcp"

**Furi** (also called **FuriOS**) is the custom real-time operating system that powers Flipper Zero. It's now integrated with AI tools via the Model Context Protocol (MCP).

## Quick Facts

- **Name**: Furi Core OS / FuriOS
- **Based On**: FreeRTOS (Real-Time Operating System)
- **Purpose**: Operating system for Flipper Zero hardware
- **Language**: C
- **Architecture**: Event-driven, multi-threaded RTOS
- **Hardware**: STM32WB55 microcontroller

## Furi Core Components (29 modules)

```
furi/core/
├── Event System        # Event loops, flags, timers
├── Threading           # Threads, mutexes, semaphores
├── Memory Management   # Heap allocator, leak detection
├── Service Registry    # Pub-sub pattern for services
├── Messaging           # Message queues, streams
├── Safety & Debugging  # Crash handling, assertions, logging
└── Kernel Abstraction  # FreeRTOS wrapper layer
```

## MCP Integration: Strawberry/Furi MCP Server

### Location
`.ai/mcp/servers/strawberry_mcp/`

### What It Does
Provides **AI-accessible tools** for Flipper Zero firmware development:

#### 4 Core Tools

1. **`build_firmware(target, app_id)`**
   - Build Flipper firmware using fbt
   - Target: f7 (Flipper Zero), f18 (future)
   - Can build full firmware or specific apps
   - Real-time build log streaming

2. **`flash_firmware()`**
   - Flash firmware to Flipper via USB
   - Automatic device detection
   - Progress monitoring

3. **`clean_firmware()`**
   - Remove all build artifacts
   - Prepare for clean rebuild

4. **`deploy_wifi_devboard_config()`**
   - Configure WiFi DevBoard V1 settings
   - Force SD card usage

### How It Works

```
User Natural Language
        ↓
  Claude Code AI
        ↓
   MCP Protocol
        ↓
Strawberry/Furi MCP Server (Python)
        ↓
fbt (Flipper Build Tool)
        ↓
Furi Core OS (C source)
        ↓
Compilation → Binary
        ↓
Flipper Zero Hardware
```

## Example Usage

### Natural Language → Firmware Build

```
👤 User: "Build and flash the Flipper firmware"

🤖 Claude:
   1. build_firmware(target="f7")
      → ./fbt updater_package TARGET=f7
      ✅ Build completed in 45.2 seconds

   2. flash_firmware()
      → ./fbt flash_usb_full
      ✅ Flash completed in 12.5 seconds

   Done! Firmware running on Flipper Zero.
```

### Build Specific Application

```
👤 User: "Build just the NFC reader app"

🤖 Claude:
   build_firmware(target="f7", app_id="applications/main/nfc")
   ✅ NFC FAP built: build/f7/applications/main/nfc/
```

## Why "Furi"?

The name "Furi" likely derives from:
- **"Fur"**nace **"I"**nternals (internal/core system)
- Or simply represents the foundational layer of Flipper firmware

It's distinct from "Flipper" (the device) and provides the OS layer that all applications run on.

## Key Features of Furi OS

### 1. Real-Time Capability
- Preemptive multitasking
- Deterministic scheduling
- Microsecond-precision timing

### 2. Safety First
```c
furi_check(condition);   // Always check, crash on fail
furi_assert(condition);  // Debug-only check
furi_crash("reason");    // Immediate crash with message
```

### 3. Event-Driven Design
- Central event loop
- Async I/O operations
- Timer-based events
- Message passing between threads

### 4. Service Architecture
```c
// Register service
furi_record_create("nfc", nfc_instance);

// Get service anywhere
Nfc* nfc = furi_record_open("nfc");
```

### 5. Memory Safety
- Tracked allocations
- Leak detection
- Thread-safe operations
- Debug heap validation

## Furi OS Architecture

```
┌─────────────────────────────────────────┐
│     Applications Layer                   │
│  (SubGHz, NFC, USB, etc.)               │
└────────────────┬────────────────────────┘
                 │
┌────────────────▼────────────────────────┐
│         Furi Core API                    │
│                                          │
│  • furi_thread_*    • furi_event_*      │
│  • furi_mutex_*     • furi_timer_*      │
│  • furi_record_*    • furi_log_*        │
│  • furi_alloc()     • furi_check()      │
└────────────────┬────────────────────────┘
                 │
┌────────────────▼────────────────────────┐
│       FreeRTOS Kernel                    │
│  (Task scheduler, Queues, Timers)       │
└────────────────┬────────────────────────┘
                 │
┌────────────────▼────────────────────────┐
│       Hardware Abstraction (HAL)         │
│       furi_hal_* APIs                    │
└────────────────┬────────────────────────┘
                 │
┌────────────────▼────────────────────────┐
│    STM32WB55 Hardware (ARM Cortex-M4)   │
└──────────────────────────────────────────┘
```

## File Structure

```
Momentum-Firmware/
├── furi/                    # Furi Core OS
│   ├── core/               # Core components (29 headers, 20 impl)
│   ├── furi.h              # Main public API
│   ├── furi.c              # Initialization
│   └── flipper.c/h         # Flipper-specific code
│
├── applications/           # User applications
│   ├── main/              # Built-in apps (NFC, SubGHz, etc.)
│   └── external/          # External/custom apps (FAPs)
│
├── furi_hal/              # Hardware abstraction layer
│
├── .ai/                   # AI integration
│   └── mcp/
│       └── servers/
│           └── strawberry_mcp/  # Furi MCP server
│               ├── main.py
│               └── furi_utils.py
│
└── fbt                    # Flipper Build Tool
```

## Configuration

### MCP Server Config (in ~/.claude.json)

```json
{
  "strawberry-furi-mcp": {
    "command": "/path/to/.venv/bin/python",
    "args": [
      "/path/to/.ai/mcp/servers/strawberry_mcp/main.py"
    ],
    "env": {
      "PYTHONPATH": "/path/to/.ai/mcp/servers/strawberry_mcp"
    }
  }
}
```

### Build Targets

- **f7**: Flipper Zero (STM32WB55)
- **f18**: Future hardware variants

## Logs & Debugging

All MCP operations are logged:

```
.ai/logs/strawberry_mcp/
├── mcp-build.log              # Latest build
├── mcp-build-TIMESTAMP.log    # Historical builds
├── mcp-flash.log              # Latest flash
├── mcp-flash-TIMESTAMP.log    # Historical flashes
├── mcp-build-live.log         # Real-time streaming
└── mcp-clean.log              # Clean operations
```

## Testing

The MCP servers have been tested end-to-end:

```bash
.ai/test_mcp_servers.sh

Results:
✅ ESP-IDF MCP: PASSED
✅ ESP RainMaker MCP: PASSED
✅ ESP MCP Local: PASSED
✅ Strawberry/Furi MCP: PASSED
```

## Development Workflow

### Traditional
```
1. Write code
2. Run: ./fbt build
3. Check output
4. Run: ./fbt flash_usb_full
5. Test on device
```

### With AI MCP
```
1. Write code
2. Say: "Build and flash the firmware"
3. AI handles build, monitors progress, flashes device
4. AI reports success/errors with context
5. Test on device
```

## Comparison: Furi vs Standard RTOS

| Feature | Standard RTOS | Furi OS |
|---------|---------------|---------|
| Thread API | Low-level | High-level wrappers |
| Memory | malloc/free | Tracked allocations |
| Events | Manual flags | Unified event loop |
| Services | None | Service registry |
| Debugging | Basic | Comprehensive crash handling |
| Type Safety | Manual | Compile-time checks |
| Documentation | External | Integrated with AI |

## Key Advantages

### For Developers
- 🎯 **Safety**: Crash early on errors, preserve debug info
- 🔄 **Services**: Easy inter-component communication
- 📊 **Logging**: Comprehensive, thread-safe logging
- 🧵 **Threading**: High-level thread management
- 🔍 **Debugging**: Rich crash reports with stack traces

### For AI Integration
- 🗣️ **Natural Language**: Build/flash via conversation
- 📝 **Context Aware**: AI reads build logs, understands errors
- ⚡ **Fast Iteration**: Quick build-test-debug cycles
- 🤖 **Automated**: AI can trigger builds, analyze results
- 📚 **Documentation**: AI has Furi API knowledge built-in

## Related Documentation

1. **FURI_CORE_OS_MCP.md** - Deep dive into Furi architecture
2. **FURI_MCP_QUICK_REFERENCE.md** - Quick command examples
3. **MCP_SERVERS_SETUP.md** - Complete MCP setup guide
4. **FuriCheck.md** - Runtime assertion system
5. **FuriHalBus.md** - Hardware abstraction details

## Summary

**Furi Core OS** is a sophisticated RTOS for Flipper Zero that:
- Provides high-level abstractions over FreeRTOS
- Emphasizes safety and debuggability
- Integrates with AI via the Strawberry/Furi MCP server
- Enables natural language firmware development
- Powers all Flipper Zero applications

The **AI MCP integration** transforms firmware development from manual command-line operations into conversational interactions, making the development process more accessible and efficient.

---

**The "furios" you mentioned = "Furi OS" = Core operating system of Flipper Zero, now AI-accessible via MCP! 🚀**
