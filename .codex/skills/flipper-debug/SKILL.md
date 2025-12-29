---
name: flipper-debug
description: Debug Flipper Zero applications and firmware issues
metadata:
  short-description: Troubleshoot and debug Flipper Zero development issues
---

# Flipper Debug

Debug Flipper Zero applications and firmware issues using available tools and techniques.

## Context

- Flipper Zero runs on STM32WB55 microcontroller
- Uses FreeRTOS operating system
- Limited debugging capabilities compared to desktop development
- Serial console available via CLI

## Debugging Tools

1. **Serial CLI:**
   - Connect via `scripts/serial_cli.py`
   - Use `log` command to view system logs
   - `free` command shows memory usage
   - `ps` shows running processes

2. **Log System:**
   ```c
   FURI_LOG_E(TAG, "Error message");
   FURI_LOG_W(TAG, "Warning message");
   FURI_LOG_I(TAG, "Info message");
   FURI_LOG_D(TAG, "Debug message");
   ```

3. **Memory Debugging:**
   - Use `memmgr_heap_printf_free_blocks()` to check heap
   - Monitor stack usage with `furi_thread_get_stack_space()`
   - Check for memory leaks with allocation tracking

## Common Issues and Solutions

1. **App Crashes:**
   - Check for null pointer dereferences
   - Verify proper memory allocation/deallocation
   - Ensure GUI elements are properly cleaned up
   - Check stack overflow (increase stack_size in application.fam)

2. **GUI Issues:**
   - Verify view_dispatcher is properly configured
   - Check scene transitions and cleanup
   - Ensure proper event handling
   - Validate input parameters

3. **Hardware Issues:**
   - Check GPIO pin configurations
   - Verify SPI/I2C initialization
   - Test with known working hardware
   - Use oscilloscope for signal analysis

## Debugging Process

1. **Reproduce the issue consistently**
2. **Add logging at key points**
3. **Check memory usage and leaks**
4. **Use CLI tools for system state**
5. **Test with minimal code to isolate problem**
6. **Review similar working code in codebase**

## Hardware Debugging

- Use SWD debugger with OpenOCD
- ST-Link or Black Magic Probe supported
- GDB debugging available with proper setup
- Check `scripts/debug/` for configuration files