# Issue #2031: Don't attach the device name in all BLE advertising packages

**Original Issue:** [https://github.com/flipperdevices/flipperzero-firmware/issues/2031](https://github.com/flipperdevices/flipperzero-firmware/issues/2031)
**Author:** @Semper-Viventem
**Created:** 2022-11-20T01:10:38Z
**Labels:** Feature Request, Bluetooth

## Description

### Describe the enhancement you're suggesting.

Currently, the BLE in the flipper is constantly broadcasting the static address and device name (including the unique flipper's name) to the BLE ether in all advertising packages. This is not a vulnerability but makes a risk of snooping on device owners. For example, any BLE-sniffer botnet in a city can track the movement of devices and compromise the owner's home address.

There are two things that will help reduce the risk:
* Add device name only in the pairing mode.
* Use a `Random Private Resolvable Address` for BLE packages.

For example, all apple devices change BLE addresses every 15 minutes to avoid the risks of surveillance.

### Anything else?

_No response_

---
*This issue was automatically imported from the upstream Flipper Zero firmware repository.*
