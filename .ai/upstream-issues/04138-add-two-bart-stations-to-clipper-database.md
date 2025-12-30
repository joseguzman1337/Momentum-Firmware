# Issue #4138: Add two BART Stations to Clipper Database

**Original Issue:** [https://github.com/flipperdevices/flipperzero-firmware/issues/4138](https://github.com/flipperdevices/flipperzero-firmware/issues/4138)
**Author:** @Davis-P0
**Created:** 2025-03-04T12:44:37Z
**Labels:** Feature Request, NFC

## Description

### Describe the enhancement you're suggesting.

There are two stations missing from the BART Station list in 
applications/main/nfc/plugins/supported_cards/clipper.c

{.id = 0x0031, .name = "Pittsburg Center"}, // Assumed - only one missing
{.id = 0x0032, .name = "Antioch"} // Verified

I can take a trip to Pittsburg Center to verify the code, if you wish.  I work for BART and sometimes use Antioch, and that code comes up as 0x0032 on my card.

Thanks for creating the project.

--Dave P


### Anything else?

_No response_

---
*This issue was automatically imported from the upstream Flipper Zero firmware repository.*
