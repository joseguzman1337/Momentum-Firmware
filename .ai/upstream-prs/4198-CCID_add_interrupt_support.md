# PR #4198: CCID: add interrupt support

## Metadata
- **Author:** @kidbomb (Filipe Paz Rodrigues)
- **Created:** 2025-04-19
- **Status:** Open
- **Source Branch:** `ccid-interrupt-dev`
- **Target Branch:** `dev`
- **URL:** https://github.com/flipperdevices/flipperzero-firmware/pull/4198

## Labels
`USB`

## Description
# What's new

Allow emulated smartcard to be inserted or removed by calling the following functions:
 - furi_hal_usb_ccid_insert_smartcard
 - furi_hal_usb_ccid_remove_smartcard

These functions will use the interrrupt endpoint to send a notify change message

# Verification 
- On linux, stop pcscd (sudo systemctl stop pcscd.socket)
- Open pcscd in daemon mode (sudo pcscd -a -f -d)
- Open ccid_test application
- Click in Remove Smartcard
- Click in Insert Smartard

You should see the following messages:

```
02404430 [136383893079616] eventhandler.c:358:EHStatusHandlerThread() **Card Removed From Generic USB Smart Card Reader 00 00**
02805751 [136383893079616] ifdhandler.c:1216:IFDHPowerICC() action: PowerUp, usb:076b/3a21:libudev:0:/dev/bus/usb/003/024 (lun: 0)
00000417 [136383893079616] eventhandler.c:406:EHStatusHandlerThread() powerState: POWER_STATE_POWERED
00000018 [136383893079616] eventhandler.c:423:EHStatusHandlerThread() **Card inserted into Generic USB Smart Card Reader 00 00**
00000010 [136383893079616] Card ATR: 3B 00 
00400853 [136383893079616] ifdhandler.c:1216:IFDHPowerICC() action: PowerDown, usb:076b/3a21:libudev:0:/dev/bus/usb/003/024 (lun: 0)
00001381 [136383893079616] eventhandler.c:482:EHStatusHandlerThread() powerState: POWER_STATE_UNPOWERED
```

# Checklist (For Reviewer)

- [ ] PR has description of feature/bug or link to Confluence/Jira task
- [ ] Description contains actions to verify feature/bugfix
- [ ] I've built this code, uploaded it to the device and verified feature/bugfix


---
*This PR tracking file was automatically generated from upstream flipperdevices/flipperzero-firmware*
