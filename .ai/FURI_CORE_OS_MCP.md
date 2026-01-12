# Furi Core OS - Flipper Zero AI MCP Integration

## What is Furi?

**Furi** is the custom real-time operating system (RTOS) for Flipper Zero, built on top of FreeRTOS. It provides a comprehensive API and framework for developing applications on the Flipper Zero hardware platform.

The name "Furi" is derived from "**Fur**nace **I**nternals" or simply refers to the core/foundational layer of the Flipper firmware.

## Architecture Overview

### Core Components

Furi consists of 29 header files and 20 implementation files in `furi/core/`:

```
furi/
├── core/                    # Core OS components (29 headers, 20 implementations)
│   ├── base.h
│   ├── check.c/h           # Runtime checks and crash handling
│   ├── common_defines.h
│   ├── core_defines.h
│   ├── dangerous_defines.h
│   ├── event_flag.c/h      # Event synchronization
│   ├── event_loop.c/h      # Main event loop system
│   ├── kernel.c/h          # Kernel abstraction layer
│   ├── log.c/h             # Logging system
│   ├── memmgr.c/h          # Memory management
│   ├── memmgr_heap.c/h     # Heap allocator
│   ├── message_queue.c/h   # Inter-thread messaging
│   ├── mutex.c/h           # Mutual exclusion primitives
│   ├── pubsub.c/h          # Publish-subscribe pattern
│   ├── record.c/h          # Service registry
│   ├── semaphore.c/h       # Semaphore primitives
│   ├── thread.c/h          # Thread management
│   ├── thread_list.c/h     # Thread tracking
│   ├── timer.c/h           # Timer services
│   ├── string.c/h          # String utilities
│   └── stream_buffer.c/h   # Stream buffering
├── furi.c                   # Main Furi initialization
├── furi.h                   # Public API header
└── flipper.c/h              # Flipper-specific code
```

## Key Features

### 1. **FreeRTOS Foundation**

Furi is built on FreeRTOS, providing:
- Preemptive multitasking
- Real-time scheduling
- Thread management
- Synchronization primitives

```c
void furi_init(void) {
    furi_check(!furi_kernel_is_irq_or_masked());
    furi_check(xTaskGetSchedulerState() == taskSCHEDULER_NOT_STARTED);

    furi_thread_init();
    furi_log_init();
    furi_record_init();
}

void furi_run(void) {
    vTaskStartScheduler();  // Start FreeRTOS scheduler
}
```

### 2. **Event Loop System**

Comprehensive event-driven programming model:
- Event flags for synchronization
- Event loops for async I/O
- Timer events
- Message queues

### 3. **Memory Management**

- Custom heap allocator
- Memory protection
- Leak detection in debug builds
- Thread-safe allocation

### 4. **Service Registry (Records)**

A publish-subscribe pattern for system services:
- Services can be registered/discovered by name
- Type-safe service access
- Dependency management

### 5. **Logging System**

Structured logging with:
- Multiple log levels
- Thread-safe operation
- Persistent crash logs
- Debug/production variants

### 6. **Safety & Debugging**

Runtime assertion system (`furi_check`, `furi_assert`):
- Crashes system on critical errors
- Preserves crash state for analysis
- Saves crash info to RTC memory
- Automatic debugger halt

## AI MCP Integration

### Strawberry/Furi MCP Server

Location: `.ai/mcp/servers/strawberry_mcp/`

This MCP server provides AI-accessible tools for Furi/Flipper Zero development:

#### Tools Provided:

1. **`build_firmware(target, app_id)`**
   - Builds Flipper Zero firmware using fbt
   - Supports different targets (f7, f18, etc.)
   - Can build specific applications
   - Real-time streaming of build logs

2. **`flash_firmware()`**
   - Flashes firmware to Flipper via USB
   - Uses `fbt flash_usb_full`
   - Provides timing and status info

3. **`clean_firmware()`**
   - Cleans build artifacts
   - Resets build environment

4. **`deploy_wifi_devboard_config()`**
   - Configures WiFi DevBoard settings
   - Ensures SD card usage for WiFi operations

#### Implementation Details:

The MCP server uses **furi_utils.py** which provides:

```python
async def run_command_async(command: str) -> Tuple[int, str, str]:
    """Run fbt/Furi commands asynchronously"""
    # Returns: (return_code, stdout, stderr)

async def run_command_async_stream(command: str, log_path: str):
    """Stream command output to log file in real-time"""
    # Useful for monitoring long-running builds
```

### Integration Architecture

```
┌─────────────────────────────────────────┐
│          Claude Code AI                 │
│      (Natural Language Interface)       │
└───────────────┬─────────────────────────┘
                │ MCP Protocol
                │
┌───────────────▼─────────────────────────┐
│      Strawberry/Furi MCP Server         │
│    (.ai/mcp/servers/strawberry_mcp)     │
│                                          │
│  Tools:                                  │
│  - build_firmware()                      │
│  - flash_firmware()                      │
│  - clean_firmware()                      │
│  - deploy_wifi_devboard_config()         │
└───────────────┬─────────────────────────┘
                │ Python subprocess
                │
┌───────────────▼─────────────────────────┐
│     Flipper Build Tool (fbt)            │
│      ./fbt [commands]                    │
└───────────────┬─────────────────────────┘
                │
┌───────────────▼─────────────────────────┐
│         Furi Core OS                     │
│    (furi/ directory)                     │
│                                          │
│  Components:                             │
│  - Event Loop                            │
│  - Thread Management                     │
│  - Memory Manager                        │
│  - Service Registry                      │
│  - HAL Abstraction                       │
└───────────────┬─────────────────────────┘
                │
┌───────────────▼─────────────────────────┐
│         FreeRTOS Kernel                  │
└───────────────┬─────────────────────────┘
                │
┌───────────────▼─────────────────────────┐
│    Flipper Zero Hardware (STM32)        │
└──────────────────────────────────────────┘
```

## Development Workflow with MCP

### Example 1: Build and Flash via AI

```
User: "Build the Flipper firmware for f7 target and flash it"

Claude (via MCP):
1. build_firmware(target="f7")
   → Executes: ./fbt updater_package TARGET=f7
   → Streams build logs in real-time
   → Returns build success/failure

2. flash_firmware()
   → Executes: ./fbt flash_usb_full
   → Flashes to connected Flipper Zero
   → Returns flash status
```

### Example 2: Build Specific App

```
User: "Build the SubGHz application"

Claude (via MCP):
build_firmware(target="f7", app_id="applications/main/subghz")
   → Executes: ./fbt fap_applications/main/subghz
   → Builds only SubGHz FAP (Flipper Application Package)
```

### Example 3: Debug Build Issues

```
User: "Clean the build and rebuild from scratch"

Claude (via MCP):
1. clean_firmware()
   → Executes: ./fbt -c
   → Removes all build artifacts

2. build_firmware(target="f7")
   → Fresh build with clean state
   → Logs saved to: .ai/logs/strawberry_mcp/mcp-build-*.log
```

## Furi API Categories

### Thread & Synchronization
- `furi_thread_*` - Thread management
- `furi_mutex_*` - Mutex operations
- `furi_semaphore_*` - Semaphore operations
- `furi_event_flag_*` - Event flags

### Event System
- `furi_event_loop_*` - Event loop management
- `furi_timer_*` - Timer services
- `furi_message_queue_*` - Message queues

### Memory
- `furi_alloc()`, `furi_free()` - Allocation
- `furi_memmgr_*` - Memory manager APIs
- `furi_string_*` - String utilities

### Services
- `furi_record_*` - Service registry
- `furi_pubsub_*` - Publish-subscribe

### Safety & Debugging
- `furi_check()` - Runtime assertion
- `furi_assert()` - Debug assertion
- `furi_crash()` - Forced crash
- `furi_halt()` - System halt
- `furi_log_*` - Logging

## Furi vs Traditional RTOS

| Feature | Traditional FreeRTOS | Furi |
|---------|---------------------|------|
| API Style | C, low-level | Higher-level abstractions |
| Memory Management | Basic malloc/free | Tracked allocations, leak detection |
| Services | Manual setup | Service registry pattern |
| Event Handling | Queues, flags | Unified event loop system |
| Debugging | Limited | Comprehensive crash analysis |
| Type Safety | Manual | Compile-time checks |

## Configuration

Furi behavior can be configured via:
- **Build targets**: f7 (Flipper Zero), f18 (future hardware)
- **Debug/Release builds**: Different assertion levels
- **Hardware abstraction**: Via furi_hal_* APIs

## Testing

Furi includes comprehensive unit tests:
```
applications/debug/unit_tests/tests/furi/
├── furi_errno_test.c
├── furi_event_loop_test.c
├── furi_memmgr_test.c
├── furi_primitives_test.c
├── furi_pubsub_test.c
├── furi_record_test.c
├── furi_stdio_test.c
├── furi_string_test.c
└── furi_test.c
```

## MCP Server Configuration

The Strawberry/Furi MCP server is configured in Claude settings:

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

## Logs and Debugging

Build and flash logs are saved to:
```
.ai/logs/strawberry_mcp/
├── mcp-build.log           # Latest build
├── mcp-build-YYYYMMDD-HHMMSS.log  # Timestamped builds
├── mcp-flash.log           # Latest flash
├── mcp-flash-YYYYMMDD-HHMMSS.log  # Timestamped flashes
└── mcp-build-live.log      # Real-time streaming log
```

## Key Advantages of Furi + MCP

1. **Natural Language Development**: Build and deploy via AI commands
2. **Automated Testing**: AI can trigger builds and analyze results
3. **Context-Aware Debugging**: AI has access to build logs and crash reports
4. **Iterative Development**: Quick build-test-debug cycles
5. **Documentation Integration**: AI can reference Furi APIs and examples

## Further Reading

- **FuriCheck.md**: Runtime checks and crash handling
- **FuriHalBus.md**: Hardware abstraction layer
- **FuriHalDebugging.md**: Debugging techniques
- **fbt.md**: Flipper Build Tool documentation

## Summary

Furi Core OS provides a robust, safety-focused RTOS framework for Flipper Zero. The integration with AI via MCP servers (Strawberry/Furi MCP) enables natural language interaction with the build system, making firmware development more accessible and efficient.

The "furios" name the user referenced is actually **Furi OS** - the core operating system that powers Flipper Zero, now accessible through AI tooling via the Model Context Protocol.
