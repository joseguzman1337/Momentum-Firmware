# Issue #4218: [Buetooth] Why is the extra beacon size limited to 31?

**Original Issue:** [https://github.com/flipperdevices/flipperzero-firmware/issues/4218](https://github.com/flipperdevices/flipperzero-firmware/issues/4218)
**Author:** @steam3d
**Created:** 2025-05-08T20:24:46Z
**Labels:** Feature Request, Bluetooth

## Description

Hi. In the main page description, it says that Flipper uses Bluetooth LE 5.4 (possibly STM32WB55), but I did not find the exact model. Does it really support only 31 bytes of beacon size?

It looks like it uses Legacy Advertising, but can we get Extended Advertising with up to 255 bytes of beacon size?

https://github.com/flipperdevices/flipperzero-firmware/blob/5b911f5405f104ad3e3051aa70e2a50a5b2a6d16/targets/f7/ble_glue/extra_beacon.c#L119

---
*This issue was automatically imported from the upstream Flipper Zero firmware repository.*
