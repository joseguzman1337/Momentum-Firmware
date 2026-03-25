# PR #4136: BadUSB: Full USB/BLE parameter customization, UI improvements, and more

## Metadata
- **Author:** @WillyJL (WillyJL)
- **Created:** 2025-03-03
- **Status:** Open
- **Source Branch:** `feat/badusb-things`
- **Target Branch:** `dev`
- **URL:** https://github.com/flipperdevices/flipperzero-firmware/pull/4136

## Labels
`USB`, `UI`, `New Feature`, `Bluetooth`

## Description
# What's new

- Backport of most features/changes from "BadKB" found on some CFW (mostly my work):
  - Full on-device customization of:
    - USB Manufacturer name
    - USB Product name
    - USB VID and PID (Vendor and Product numeric IDs)
    - BLE Device Name
    - BLE MAC Addess
    - BLE Remember (whether to save paired devices or forget them on disconnect)
    - BLE Pairing (security mode for pairing: show PIN code, PIN confirm yes/no, simple yes/no (not supported on all devices, iPhones support it))
    - Default values for these parameters respect what BadUSB used previously
  - Added commands `BLE_ID` and `BT_ID` (alias for backwards compatibility), similar to `ID` command but they set BLE MAC address and device name
  - `ID`, `BLE_ID` and `BT_ID` commands will automatically switch connection mode to their own (if user had selected USB mode, opening a script with `BLE_ID` command will switch to BLE mode on first open), can be changed after opening script of course
  - UI additions/improvements:
    - Show script elapsed/run timer
    - Show script current line / total lines below big percentage
  - Expanded allowed BLE name length to max possible based on currently used AD types/segments (calculated by dissecting BLE advertisement in wireshark, math shown for future reference in code comment)
- Added de-DE-mac and fi-FI keyboard layouts from third party contributors
- Some random cleanup

# Verification 

- Play around with BadUSB, make sure all works as expected
- Try `BLE_ID 11:22:33:44:55:AA Test123` command and see different values used
- Check custom user-input values saving (values set by `ID`/`BLE_ID`/`BT_ID` are not saved to user config)
- Check connection mode autoswitch based on `ID` and `BLE_ID`/`BT_ID` command

# Checklist (For Reviewer)

- [ ] PR has description of feature/bug or link to Confluence/Jira task
- [ ] Description contains actions to verify feature/bugfix
- [ ] I've built this code, uploaded it to the device and verified feature/bugfix


---
*This PR tracking file was automatically generated from upstream flipperdevices/flipperzero-firmware*
