# PR #4053: nfc: Attempt to detect MFP 2k in MFC mode

## Metadata
- **Author:** @GMMan (Yukai Li)
- **Created:** 2024-12-31
- **Status:** Open
- **Source Branch:** `nfc-mfc-detect-plus-2k`
- **Target Branch:** `dev`
- **URL:** https://github.com/flipperdevices/flipperzero-firmware/pull/4053

## Labels
None

## Description
# What's new

- Read extra accessible sectors on a MIFARE Plus 2k compared to MIFARE Classic 1k

# Verification 

- Read a MIFARE Plus 2k in SL1 as a MIFARE Classic card. It should be detected as a MIFARE Plus 2k.

# Checklist (For Reviewer)

- [ ] PR has description of feature/bug or link to Confluence/Jira task
- [ ] Description contains actions to verify feature/bugfix
- [ ] I've built this code, uploaded it to the device and verified feature/bugfix

Not sure whether MIFARE Plus 2k has 17 or 18 sectors. On my sample MIFARE Plus EV1 2k, sector 17 is not accessible, however that may be an effect of some sectors set to SL3. Someone with other samples will have to determine how many sectors there actually are.

Fixes #4012

---
*This PR tracking file was automatically generated from upstream flipperdevices/flipperzero-firmware*
