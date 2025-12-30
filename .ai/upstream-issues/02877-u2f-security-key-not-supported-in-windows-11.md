# Issue #2877: U2F Security Key not supported in Windows 11

**Original Issue:** [https://github.com/flipperdevices/flipperzero-firmware/issues/2877](https://github.com/flipperdevices/flipperzero-firmware/issues/2877)
**Author:** @SystemOfTheCSGO
**Created:** 2023-07-14T08:53:26Z
**Labels:** Feature Request, USB

## Description

### Describe the enhancement you're suggesting.

The current module of security key U2F is not supported by windows.

Reproduction

Use the firmware as usual, get a clean install of windows 11, try to link the security key from flipper to windows, you will get a error: this device is not certified.

### Anything else?

This can be bypassed emulating headers of a certified key. (I’ve seen it done before, at least a homemade microsoft certified’ seckey.)

---
*This issue was automatically imported from the upstream Flipper Zero firmware repository.*
