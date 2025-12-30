# PR #3723: FuriHal: static platform ID used in BLE MAC address

## Metadata
- **Author:** @skotopes (あく)
- **Created:** 2024-06-18
- **Status:** Open
- **Source Branch:** `aku/ble_mac_fix`
- **Target Branch:** `dev`
- **URL:** https://github.com/flipperdevices/flipperzero-firmware/pull/3723

## Labels
None

## Description
# What's new

- FuriHal: fixed platform ID used in BLE MAC address

# Verification 

- Last 3 octets of BLE address are always fixed
- 4th octet of `p/x furi_hal_version.ble_mac` will be 0x26 on flippers manufactured in 2023+

# Checklist (For Reviewer)

- [ ] PR has description of feature/bug or link to Confluence/Jira task
- [ ] Description contains actions to verify feature/bugfix
- [ ] I've built this code, uploaded it to the device and verified feature/bugfix


---
*This PR tracking file was automatically generated from upstream flipperdevices/flipperzero-firmware*
