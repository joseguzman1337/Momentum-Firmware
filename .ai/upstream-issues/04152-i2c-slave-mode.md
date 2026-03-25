# Issue #4152: I2C Slave mode

**Original Issue:** [https://github.com/flipperdevices/flipperzero-firmware/issues/4152](https://github.com/flipperdevices/flipperzero-firmware/issues/4152)
**Author:** @TheSainEyereg
**Created:** 2025-03-18T16:58:07Z
**Labels:** Feature Request, Core+Services

## Description

### Description of the feature you're suggesting.

I need to communicate with other devices (like ESP32 or maybe other Flippers) using I2C, so I can't always be a master.

Is there any possibility to use my Flipper Zero as I2C slave? There's no mention in furi_hal documentation about I2C slave other than communicating with it.

### Anything else?

I saw STM32WB55RG datasheet and there is no clear distinct between I2C master and slave (which wasn't mentioned at all) modes, so It's possible that the same pins are used for master and slave modes. Only thing that possibly needed is software support for I2CSL.

---
*This issue was automatically imported from the upstream Flipper Zero firmware repository.*
