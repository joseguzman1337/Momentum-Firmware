# Issue #3772: MIFARE Ultralight C hex dump shows bogus data for locked pages

**Original Issue:** [https://github.com/flipperdevices/flipperzero-firmware/issues/3772](https://github.com/flipperdevices/flipperzero-firmware/issues/3772)
**Author:** @supersat
**Created:** 2024-07-09T00:26:47Z
**Labels:** NFC, UI, Triage

## Description

### Describe the bug.

At a recent event, we gave everyone MIFARE Ultralight C wristbands with some pages locked as part of a CTF. Many people tried reading their wristband with their Flipper Zero, and unfortunately, rather than seeing some pages locked in the hex dump, they saw bogus data (seemingly copied starting from page 0). The NXP TagInfo app for Android correctly showed those pages as XX XX XX XX.

### Reproduction

1. Auth-protect some pages on a MIFARE Ultralight C card. This can be done by writing 25 00 00 00 to page 0x2a and 00 00 00 00 to page 0x2b. This locks pages 0x25 and up from being read without authentication.
2. Read the tag with the Flipper Zero.
3. Select Info, then more, then scroll down to the bottom. The last 3 pages should show as locked, but are copies of pages 0, 1, and 2.

### Target

_No response_

### Logs

_No response_

### Anything else?

FW version 0.103.1

---
*This issue was automatically imported from the upstream Flipper Zero firmware repository.*
