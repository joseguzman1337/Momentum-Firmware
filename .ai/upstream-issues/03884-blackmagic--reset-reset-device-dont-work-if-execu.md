# Issue #3884: Blackmagic: Reset/Reset Device don't work if execution is suspended on `furi_check()`

**Original Issue:** [https://github.com/flipperdevices/flipperzero-firmware/issues/3884](https://github.com/flipperdevices/flipperzero-firmware/issues/3884)
**Author:** @CookiePLMonster
**Created:** 2024-09-07T16:41:54Z
**Labels:** Build System & Scripts, Triage

## Description

### Describe the bug.

When debugging with Blackmagic (in my case, through WiFi), if the Flipper suspends on `furi_check` it appears to be impossible to reboot it. Neither Reset Device or Reset commands do anything, so the device has to be disconnected from USB and then power cycled by holding Back for 30s.

### Reproduction

1. Attach Blackmagic to FW when Flipper is connected to the PC via the USB cable (in practice, necessary for FAP development).
2. Make it crash on `furi_check()`.
3. Attempt to reset the device via a debugger.
4. Observe errors in log

### Target

f7 running stable v0.105.0 + devboard in blackmagic mode, running the latest dev FW (the one that adds UART over web)

### Logs

```Text
Waiting for gdb server to start...[2024-09-04T10:21:17.225Z] SERVER CONSOLE DEBUG: onBackendConnect: gdb-server session connected. You can switch to "DEBUG CONSOLE" to see GDB interactions.
"H:/dev/flipper-zero/.ufbt/toolchain/x86_64-windows/bin/openocd.EXE" -c "gdb_port 50000" -c "tcl_port 50001" -c "telnet_port 50002" -s "H:\\dev\\flipper-zero\\flipper-bakery\\digital_clock" -f "c:/Users/Adrian/.vscode/extensions/marus25.cortex-debug-1.12.1/support/openocd-helpers.tcl" -f interface/cmsis-dap.cfg -f "H:/dev/flipper-zero/.ufbt/current/scripts/debug/stm32wbx.cfg" -c "CDRTOSConfigure FreeRTOS"
Open On-Chip Debugger 0.12.0+dev-g708504d4b (2024-07-18-12:29)
Licensed under GNU GPL v2
For bug reports, read
        http://openocd.org/doc/doxygen/bugs.html
CDLiveWatchSetup
Info : auto-selecting first available session transport "swd". To override use 'transport select <transport>'.
Info : DEPRECATED target event trace-config; use TPIU events {pre,post}-{enable,disable}
Info : Listening on port 50001 for tcl connections
Info : Listening on port 50002 for telnet connections
c:/Users/Adrian/.vscode/extensions/marus25.cortex-debug-1.12.1/support/openocd-helpers.tcl: stm32wbx.cpu configure -rtos FreeRTOS
Error: unable to find a matching CMSIS-DAP device

[2024-09-04T10:21:17.386Z] SERVER CONSOLE DEBUG: onBackendConnect: gdb-server session closed
GDB server session ended. This terminal will be reused, waiting for next session to start...
```


### Anything else?

_No response_

---
*This issue was automatically imported from the upstream Flipper Zero firmware repository.*
