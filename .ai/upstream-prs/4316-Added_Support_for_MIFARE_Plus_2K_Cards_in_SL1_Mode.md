# PR #4316: Added Support for MIFARE Plus 2K Cards in SL1 Mode

## Metadata
- **Author:** @LuemmelSec ()
- **Created:** 2025-12-10
- **Status:** Open
- **Source Branch:** `dev`
- **Target Branch:** `dev`
- **URL:** https://github.com/flipperdevices/flipperzero-firmware/pull/4316

## Labels
None

## Description
# What's new

Added Support for MIFARE Plus 2K Cards in SL1 Mode
MIFARE Plus 2k cards in SL1 mode - emulating a MIFARE Classic card - would get recognized as MIFARE Classic 1K card and Flipper would stop checking after sector 16. However, 2k cards in SL1 mode offer more sectors, typically 2 additional ones, which Flipper would miss and break the cards and emulation if there is stuff written to these sectors that is needed for it to function.

There is now a detection logic for 2k cards and the additional sectors are also read and cam be emulated.
This is also in reference to: https://github.com/flipperdevices/flipperzero-firmware/pull/4053

# Verification 

Scan a MIFARE Plus 2K card in SL1 mode an see that only 16 sectors are scanned and Flipper detects it as MIFARE Classic 1K card.
Install the new firmware and observer that the 2K card is now correctly recognized and the additional sectors read.

<img width="817" height="420" alt="image" src="https://github.com/user-attachments/assets/d883ccd8-2a99-4ea5-8917-2a25df5550ef" />


# Checklist (For Reviewer)

- [x ] PR has description of feature/bug or link to Confluence/Jira task
- [x ] Description contains actions to verify feature/bugfix
- [x ] I've built this code, uploaded it to the device and verified feature/bugfix


---
*This PR tracking file was automatically generated from upstream flipperdevices/flipperzero-firmware*
