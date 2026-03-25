# Issue #2231: Apple magsafe emulation

**Original Issue:** [https://github.com/flipperdevices/flipperzero-firmware/issues/2231](https://github.com/flipperdevices/flipperzero-firmware/issues/2231)
**Author:** @bettse
**Created:** 2022-12-31T04:02:38Z
**Labels:** Feature Request, NFC

## Description

### Description of the feature you're suggesting.

Very low priority, but I was thinking it would be fun to have an NFC menu item for emulation an Apple magsafe device like a phone case or wallet.  Or maybe also a format so one could scan existing, save, emulate, etc.  Lots of options, very minor benefit.  The magsafe devices appear as a type 4 tag with an NDEF record, the CC file contains bytes that indicate the specific color, device type (wallet/case), etc.  They use an unusual anti-collision, in theory to prevent overlap with regular 14a NFC.  Proxmark has lots of the anti-col details (https://github.com/RfidResearchGroup/proxmark3/blob/97e394c58a649d5f74d101202a76214e5e70d596/include/protocols.h#L163), and iceman rfid discord has some example CC in the back history.

### Anything else?

_No response_

---
*This issue was automatically imported from the upstream Flipper Zero firmware repository.*
