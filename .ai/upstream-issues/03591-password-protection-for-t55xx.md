# Issue #3591: Password protection for T55xx

**Original Issue:** [https://github.com/flipperdevices/flipperzero-firmware/issues/3591](https://github.com/flipperdevices/flipperzero-firmware/issues/3591)
**Author:** @mxcdoam
**Created:** 2024-04-15T19:00:27Z
**Labels:** Feature Request, RFID 125kHz

## Description

### Description of the feature you're suggesting.

I'm talking about intercom keys. In my area it is a common countermeasure of service providers, to check if the tag is writeable. If intercom detects T55xx, it damages the tag (probably writing zeros as UID + locking or password protecting. That way tag cannot be detected and generally reused anymore). But it seems that tags password-protected by me are not detected as clones and continue to work. Right now flipper zero cannot protect tags, so I was wondering if it's possible to add this feature?

### Anything else?

_No response_

---
*This issue was automatically imported from the upstream Flipper Zero firmware repository.*
