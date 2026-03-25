# Issue #4247: NFC files not syncing via Bluetooth from Flipper to Android app (v1.8)

**Original Issue:** [https://github.com/flipperdevices/flipperzero-firmware/issues/4247](https://github.com/flipperdevices/flipperzero-firmware/issues/4247)
**Author:** @KevinLiebergen
**Created:** 2025-07-03T08:22:26Z
**Labels:** Bluetooth, Triage

## Description

### Describe the bug.

Hi, I'm currently using the Flipper Zero (v1.3.4) with the Android app (v1.8 – latest release from November 2024), and I'm having trouble syncing NFC files via Bluetooth.

The NFC files are definitely being saved on the Flipper, since I can see them when I connect the device to a computer via USB and browse the file system. However, they don't appear in the Android app.

I've tried uninstalling and reinstalling the APK, and also confirmed that RFID and SubGHz files sync correctly via Bluetooth, only NFC files are missing.

I haven't found any open issues related to this, and after a bit of searching, I couldn't find any similar reports online. Has anyone else encountered this issue or found a workaround?

Thanks in advance!

### Reproduction

1. Power on Flipper Zero and connect it to the Android app (v1.8) via Bluetooth.
2. Scan an NFC tag using the Flipper.
3. Open the Android app and go to the "NFC" section.
4. Observe that the scanned NFC file does not appear in the app.
5. Connect the Flipper to a computer via USB and browse the internal storage.
6. Confirm that the NFC file exists on the device.


---
*This issue was automatically imported from the upstream Flipper Zero firmware repository.*
