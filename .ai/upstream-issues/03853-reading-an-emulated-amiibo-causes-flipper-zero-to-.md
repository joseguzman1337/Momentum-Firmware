# Issue #3853: Reading an emulated Amiibo causes Flipper Zero to crash using NFC read but works using NFC Read specific card type

**Original Issue:** [https://github.com/flipperdevices/flipperzero-firmware/issues/3853](https://github.com/flipperdevices/flipperzero-firmware/issues/3853)
**Author:** @ukscone
**Created:** 2024-08-24T16:28:49Z
**Labels:** NFC, Triage

## Description

### Describe the bug.

When trying to read an emulated Amiibo from a device like the Flashiibo (https://www.flashiibo.com/) or Maleen NFC Tag Generator that uses an nRF52832 to emulate NTAG N215 tags the Flipper zero crashes and reboots with a furi_check failed error & the last line in the logs in debug or trace mode is "[D][NfcScanner] Found 5 children" when using the NFC Read but when using NFC->Extra Actions->Read Specific Card Type as either iso14443-3a or NTAG it works as expected.

### Reproduction

Apps->NFC->NFC->Read then hold a multi-ntag emulator device to the back of the flipper and watch the flipper screen darken and then "reboot" with a flipper crashed and was rebooted furi_check failed message 

### Target

_No response_

### Logs

_No response_

### Anything else?

_No response_

---
*This issue was automatically imported from the upstream Flipper Zero firmware repository.*
