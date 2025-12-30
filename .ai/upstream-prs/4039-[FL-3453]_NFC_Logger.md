# PR #4039: [FL-3453] NFC Logger

## Metadata
- **Author:** @RebornedBrain ()
- **Created:** 2024-12-19
- **Status:** Open
- **Source Branch:** `reborned/nfc_logger_plugin`
- **Target Branch:** `dev`
- **URL:** https://github.com/flipperdevices/flipperzero-firmware/pull/4039

## Labels
`NFC`, `New Feature`

## Description
# What's new

- Now NFC library can save log traces while it works. This traces can help debugging and see whats going on.
- NFC application now has logger formatter which is done as a plugin and loaded dynamicaly
- Several different modes for formatting can be set.

> [!NOTE]
> Now all protocols saves their history as binary data, but they need protocol specific formatters to be added, in order to be
displayed in human readable format. Below there is a list of protocols which are now formatted.

### Supported protocols:
- [x] iso14443_3a
- [x] iso14443_3b
- [x] iso14443_4a
- [x] iso14443_4b
- [x] MfUltralight
- [x] Felica
- [x] MfClassic
- [x] Desfire
- [x] MfPlus
- [x] iso15693_3
- [x] Slix
- [x] St25tb

# ToDo:
- [x] Add formatters for all other protocols in both poller and listener modes
- [x] Add MfClassic protocol
- [ ] Make formatting more simplified and informative (should be done for each protocol separately)
- [x] Add logger config buttons to Debug scene in NFC app 

# Verification 

By default logger is disabled and doesn't impact NFC flow.
- Run NFC app and go to Debug menu
- Press "Enable Logger" button, it will switch to "Disable Logger" now logger is active.

### Poller test:
- Try to read any of supported protocols Ultralight for example
- Once done, connect Flipper to PC and go to `ext/nfc/log`
- Download txt file with latest datetime in format `LOG-yyyymmdd-hhmmss.txt`, you will see logs

### Listener test:
- Try to emulate any of supported protocols Ultralight for example
- Try to read your emulation
- Stop emulation
- Connect Flipper to PC and go to `ext/nfc/log`
- Download txt file with latest datetime in format `LOG-yyyymmdd-hhmmss-n.txt`, you will see logs

# Checklist (For Reviewer)

- [ ] PR has description of feature/bug or link to Confluence/Jira task
- [ ] Description contains actions to verify feature/bugfix
- [ ] I've built this code, uploaded it to the device and verified feature/bugfix


---
*This PR tracking file was automatically generated from upstream flipperdevices/flipperzero-firmware*
