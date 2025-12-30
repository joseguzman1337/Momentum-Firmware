# PR #2658: Hitag

## Metadata
- **Author:** @blackvault88 ()
- **Created:** 2023-05-10
- **Status:** Open
- **Source Branch:** `hitag`
- **Target Branch:** `dev`
- **URL:** https://github.com/flipperdevices/flipperzero-firmware/pull/2658

## Labels
`RFID 125kHz`, `UI`, `New Feature`

## Description
# What's new

- Included support for RTF (Reader Talks First) mode in RFID app, both for read & emulate modes.
- Included the Hitag1 protocol as first RTF protocol (more to come later, like Hitag2, HitagS) supporting read & emulate of public non encrypted pages 
- Updated the RFID scenes & views accordingly
- Updated the RFID key file save & load functions, by adding 'Hitag1 specific data' after the general section (fully backwards compatible with existing keys)

# Verification 

- Run RFID app and read/emulate/save/view/edit any of the already supported protocols
- Run RFID app and read/emulate/save a new Hitag1 card 
- Run RFID app and emulate/view/edit a saved Hitag1 card (sample key files for verification are added below)
[sampleHitag1.zip](https://github.com/flipperdevices/flipperzero-firmware/files/11441497/sampleHitag1.zip)

# Checklist (For Reviewer)

- [ ] PR has description of feature/bug or link to Confluence/Jira task
- [ ] Description contains actions to verify feature/bugfix
- [ ] I've built this code, uploaded it to the device and verified feature/bugfix


---
*This PR tracking file was automatically generated from upstream flipperdevices/flipperzero-firmware*
