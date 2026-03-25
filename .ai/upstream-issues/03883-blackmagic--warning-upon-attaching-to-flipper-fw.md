# Issue #3883: Blackmagic: Warning upon attaching to Flipper FW

**Original Issue:** [https://github.com/flipperdevices/flipperzero-firmware/issues/3883](https://github.com/flipperdevices/flipperzero-firmware/issues/3883)
**Author:** @CookiePLMonster
**Created:** 2024-09-07T16:38:05Z
**Labels:** Build System & Scripts, Triage

## Description

### Describe the bug.

`warning: could not convert 'FlipperApplication' from the host encoding (CP1252) to UTF-32. This normally should not happen, please file a bug report.` warning appears in the debug console upon attaching Blackmagic. This doesn't appear to have any side effects, but might be worth checking out regardless.

### Reproduction

1. Set up uFBT on a Windows machine with a Windows-1252 (Central Europe) codepage.
2. In VSCode, use `Attach FW (blackmagic).
3. Observe the warning.

### Target

f7 running stable v0.105.0 + devboard in blackmagic mode, running the latest dev FW (the one that adds UART over web)

### Logs

```Text
Cortex-Debug: VSCode debugger extension version 1.12.1 git(652d042). Usage info: https://github.com/Marus/cortex-debug#usage
Reading symbols from H:/dev/flipper-zero/.ufbt/toolchain/x86_64-windows/bin/arm-none-eabi-objdump.exe --syms -C -h -w H:/dev/flipper-zero/.ufbt/current/firmware.elf
Reading symbols from h:/dev/flipper-zero/.ufbt/toolchain/x86_64-windows/bin/arm-none-eabi-nm.exe --defined-only -S -l -C -p H:/dev/flipper-zero/.ufbt/current/firmware.elf
Launching GDB: "H:/dev/flipper-zero/.ufbt/toolchain/x86_64-windows/bin/arm-none-eabi-gdb-py3.EXE" -q --interpreter=mi2
    IMPORTANT: Set "showDevDebugOutput": "raw" in "launch.json" to see verbose GDB transactions here. Very helpful to debug issues or report problems
Finished reading symbols from objdump: Time: 80 ms
Output radix now set to decimal 16, hex 10, octal 20.
Input radix now set to decimal 10, hex a, octal 12.
Cortex-M timeout to wait for device halts: 2000
Available Targets:
No. Att Driver
 1      STM32WBxx (secure) M4
Attaching to program: H:\dev\flipper-zero\.ufbt\current\firmware.elf, Remote target
Finished reading symbols from nm: Time: 691 ms
vPortSuppressTicksAndSleep (expected_idle_ticks=0xa1) at targets/f7/furi_hal/furi_hal_os.c:172
172	targets/f7/furi_hal/furi_hal_os.c: No such file or directory.
Program stopped, probably due to a reset and/or halt issued by debugger
Firmware version on attached Flipper:
	Version:     0.105.0
	Built on:    15-08-2024
	Git branch:  0.105.0
	Git commit:  8ea6a3df
	Dirty:       False
	HW Target:   7
	Origin:      Official
	Git origin:  https://github.com/flipperdevices/flipperzero-firmware
Support for Flipper external apps debug is loaded
Set 'H:/dev/flipper-zero/.ufbt/build' as debug info lookup path for Flipper external apps
Attaching to Flipper firmware
warning: could not convert 'FlipperApplication' from the host encoding (CP1252) to UTF-32.
This normally should not happen, please file a bug report.
```


### Anything else?

_No response_

---
*This issue was automatically imported from the upstream Flipper Zero firmware repository.*
