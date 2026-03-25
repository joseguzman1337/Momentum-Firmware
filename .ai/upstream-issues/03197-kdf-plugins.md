# Issue #3197: KDF plugins

**Original Issue:** [https://github.com/flipperdevices/flipperzero-firmware/issues/3197](https://github.com/flipperdevices/flipperzero-firmware/issues/3197)
**Author:** @noproto
**Created:** 2023-11-04T15:05:52Z
**Labels:** Feature Request, NFC

## Description

### Describe the enhancement you're suggesting.

A significant enhancement for the NFC app would be an interface to allow libraries/shared objects to be registered (or loaded from a fixed SD card path) which could be used as custom dictionaries for bruteforce attacks. This is particularly useful for key derivation functions (KDFs).

As discussed on the Q&A, we're hoping to identify an ideal location/API to implement this which would be compatible with multiple NFC protocols without duplicating code - such as MIFARE Classic, DESFire, and Ultralight C. Either C or JavaScript functions can be written for use with this handler. The external function is loaded from the SD card and called with the known card parameters (e.g. ATQA, SAK, CUID), which returns an array of zero or more keys. Each key is tested as a part of the overall dictionary attack against the card.

This approach ensures that the firmware remains free from copyrighted or proprietary algorithms, while (often) eliminating more advanced NFC attacks such as MFKey or Nested.

### Anything else?

_No response_

---
*This issue was automatically imported from the upstream Flipper Zero firmware repository.*
