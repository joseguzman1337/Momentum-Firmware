# Issue #3939: readKeyState function for badusb mjs module

**Original Issue:** [https://github.com/flipperdevices/flipperzero-firmware/issues/3939](https://github.com/flipperdevices/flipperzero-firmware/issues/3939)
**Author:** @mantacid
**Created:** 2024-10-11T18:13:16Z
**Labels:** Feature Request, JS

## Description

### Describe the enhancement you're suggesting.

The firmware of most external keyboards allows the keyboard to receive signals from the device to which it is connected, in order to update the status LEDs for the caps-lock, num-lock, and scroll-lock keys. This could be a useful method of data exfiltration in airgapped systems: if the flipper zero could read the state of a virtual keyboard, a badusb payload could install and execute a script on the target machine that uses these keys to send data directly to the flipper itself.

The feature could take the form of a `readKeyState()` method in the JavaScript `badusb` module, or even a separate method for each key.

### Anything else?

_No response_

---
*This issue was automatically imported from the upstream Flipper Zero firmware repository.*
