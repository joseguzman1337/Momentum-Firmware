# Issue #2563: U2F does not work with some services

**Original Issue:** [https://github.com/flipperdevices/flipperzero-firmware/issues/2563](https://github.com/flipperdevices/flipperzero-firmware/issues/2563)
**Author:** @JulyIghor
**Created:** 2023-04-05T01:45:29Z
**Labels:** USB, Bug

## Description

### Describe the bug.

Flipper Zero's U2F does not work with Facebook via a web browser

### Reproduction

1. Open Safari, macOS
2. Visit facebook.com
3. Try to add Flipper Zero's U2F as a security key
4. You get infinite load instead of the key to be added

### Target

U2F do work with Facebook

### Anything else?

YubiKey works as expected with Facebook, but Flipper Zero can't be added in any case.
Flipper Zero U2F working fine with GMail

---
*This issue was automatically imported from the upstream Flipper Zero firmware repository.*
