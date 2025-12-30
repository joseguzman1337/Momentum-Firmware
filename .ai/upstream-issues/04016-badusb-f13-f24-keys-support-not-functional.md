# Issue #4016: BadUSB F13-F24 keys support not functional

**Original Issue:** [https://github.com/flipperdevices/flipperzero-firmware/issues/4016](https://github.com/flipperdevices/flipperzero-firmware/issues/4016)
**Author:** @jezh42
**Created:** 2024-11-25T03:41:48Z
**Labels:** Feature Request, USB

## Description

### Describe the bug.

When trying to use BadUsb and badusb-js on the latest version of the firmware, I am unable to properly emulate the F13-F24 keys. Support for these keys were apparently added back in [March](https://github.com/flipperdevices/flipperzero-firmware/pull/3468), and the code has not been removed since. 
When executing a BadUsb script with F1->F24 connected to a Windows or Linux machine, with a supported keyboard input program monitoring keypresses, I am unable to register any of the F13-F24 keys.
Using other software, such as AutoHotKey, I am able to register F13-F24, so the monitoring program is not the issue. Furthermore, Windows has support for F13-F24 shortcuts, such as the default enabled Win + F21 opening settings, which I am also unable to emulate through Flipper BadUsb.
I have tried using badusb-js as well, trying F13-F24 directly, HID decimal and HID hex and no success.



### Reproduction

1. Create a BadUsb script containing F13 up to F24, each on new lines, followed by "GUI F21" on the final line
2. Copy script to Flipper
3. Plug Flipper into a Windows computer via USB
4. Open a keyboard tester program that supports F13-F24
5. Execute the BadUsb script via Flipper
6. Notice the keypresses triggered, only the GUI key will be executed

### Target

_No response_

### Logs

_No response_

### Anything else?

_No response_

---
*This issue was automatically imported from the upstream Flipper Zero firmware repository.*
