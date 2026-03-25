# Issue #4258: Internal GDB error when trying to flash firmware using wifi devboard

**Original Issue:** [https://github.com/flipperdevices/flipperzero-firmware/issues/4258](https://github.com/flipperdevices/flipperzero-firmware/issues/4258)
**Author:** @MatthewTromp
**Created:** 2025-07-31T17:59:50Z
**Labels:** Triage

## Description

### Describe the bug.

I'm trying to use the devboard to debug an application, following this guide: https://developer.flipper.net/flipperzero/doxygen/dev_board_debugging_guide.html
With the devboard plugged in via usb (and itself plugged into the flipper zero of course), when running `./fbt flash`, I get an error, the screen on my flipper zero freezes and then goes dark and won't turn back on. I have to put it into firmware recovery mode to get it back. Here's the error:
```
sbaugh@moon:~/src/flipperzero-firmware$ ./fbt flash
	SDKCHK	targets/f7/api_symbols.csv
API version 86.0 is up to date
python3 scripts/fwflash.py --interface=auto --serial=auto build/f7-firmware-D/firmware.elf
2025-07-31 13:44:39,230 [INFO] Probing for local interfaces...
2025-07-31 13:44:39,309 [INFO] Using blackmagic_usb
2025-07-31 13:44:39,309 [INFO] Flashing /home/sbaugh/src/flipperzero-firmware/build/f7-firmware-D/firmware.elf
......
2025-07-31 13:44:40,811 [ERROR] Blackmagic failed to flash
2025-07-31 13:44:40,812 [ERROR] GNU gdb (GDB) 13.2
Copyright (C) 2023 Free Software Foundation, Inc.
License GPLv3+: GNU GPL version 3 or later <http://gnu.org/licenses/gpl.html>
This is free software: you are free to change and redistribute it.
There is NO WARRANTY, to the extent permitted by law.
Type "show copying" and "show warranty" for details.
This GDB was configured as "--host=x86_64-pc-linux-gnu --target=arm-none-eabi".
Type "show configuration" for configuration details.
For bug reporting instructions, please see:
<https://www.gnu.org/software/gdb/bugs/>.
Find the GDB manual and other documentation resources online at:
    <http://www.gnu.org/software/gdb/documentation/>.

For help, type "help".
Type "apropos word" to search for commands related to "word"...
Reading symbols from /home/sbaugh/src/flipperzero-firmware/build/f7-firmware-D/firmware.elf...
Remote debugging using /dev/ttyACM0
Available Targets:
No. Att Driver
 1      STM32WBxx M4
Attaching to program: /home/sbaugh/src/flipperzero-firmware/build/f7-firmware-D/firmware.elf, Remote target
/toolchain/src/src/gdb-13.2/gdb/thread.c:85: internal-error: inferior_thread: Assertion `current_thread_ != nullptr' failed.
A problem internal to GDB has been detected,
further debugging may prove unreliable.
----- Backtrace -----
0x604d847e4151 ???
0x604d84b227b4 ???
0x604d84b22a7a ???
0x604d84c352b1 ???
0x604d84ada35b ???
0x604d84adab12 ???
0x604d849ce9e9 ???
0x604d849812cd ???
0x604d84adf23e ???
0x604d84a34c85 ???
0x604d84a4c257 ???
0x604d84960da3 ???
0x604d84817204 ???
0x604d84ae5dab ???
0x604d849abf95 ???
0x604d849ac061 ???
0x604d849ad644 ???
0x604d849ae13a ???
0x604d8471fceb ???
0x7fc53062a1c9 __libc_start_call_main
	../sysdeps/nptl/libc_start_call_main.h:58
0x7fc53062a28a __libc_start_main_impl
	../csu/libc-start.c:360
0x604d84726769 ???
0xffffffffffffffff ???
---------------------

This is a bug, please report it.  For instructions, see:
<https://www.gnu.org/software/gdb/bugs/>.
2025-07-31 13:44:40,812 [ERROR] Failed to flash via blackmagic_usb
scons: *** [build/flash.flag] Error 1

********** FBT ERRORS **********
build/flash.flag: Error 1
```
My wifi devboard's LED is currently red. It was originally blue, but I couldn't get it to do anything so I held the boot button for 10 seconds and the led changed to red and hasn't changed back since. I don't know the significance of this.

### Reproduction

1. Acquire a fresh wifi devboard
2. Plug it into your computer via USB and hold the boot button for 10 seconds until the LED switches from blue to red
3. Plug the devboard into your flipper zero
4. Follow the steps here: https://developer.flipper.net/flipperzero/doxygen/dev_board_debugging_guide.html, selecting "Attach FW (blackmagic)" in step 4 of "Debugging the firmware", until step 5 of that section
5. Run `./fbt flash` and note the error

### Target

_No response_

### Logs

```Text

```

### Anything else?

_No response_

---
*This issue was automatically imported from the upstream Flipper Zero firmware repository.*
