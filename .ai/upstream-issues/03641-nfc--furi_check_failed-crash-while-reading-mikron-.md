# Issue #3641: NFC: furi_check_failed crash while reading MIKRON NFC on 0.101.2

**Original Issue:** [https://github.com/flipperdevices/flipperzero-firmware/issues/3641](https://github.com/flipperdevices/flipperzero-firmware/issues/3641)
**Author:** @mxcdoam
**Created:** 2024-05-08T18:23:16Z
**Labels:** NFC, Triage

## Description

### Describe the bug.

I get a crash while trying to read a card with MICRON JSC's implenetation of Ultralight: cards wich were not personalized (issued to an end user) are reporting to have 41 pages, and are read properly. Issued cards are reporting to have 16 pages and cause a crash on FW 0.101.2. I downgraded FZ to check those cards on FW 0.99.1, and both types (issued and not issued) were working properly and were not causing a crash. I've attached three dumps: 1)"Perso" aquired on 0.99.1, crashes 0.101.2, flipper recognize it as "Ultralight"; 2)Preperso aquired on 0.99.1, works fine, Fliper recognize it as "Ultralight 21"; 3) Same card as preperso aquired on 0.101.2.
[FFF dumps.zip](https://github.com/flipperdevices/flipperzero-firmware/files/15253224/FFF.dumps.zip)


### Reproduction

Update FW to 0.101.2
Try to read MIKRON NFC tag 

### Target

_No response_

### Logs

_No response_

### Anything else?

_No response_

---
*This issue was automatically imported from the upstream Flipper Zero firmware repository.*
