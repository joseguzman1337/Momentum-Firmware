# Issue #3835: Attempting to read DESFire Card causes `furi_check()` crash

**Original Issue:** [https://github.com/flipperdevices/flipperzero-firmware/issues/3835](https://github.com/flipperdevices/flipperzero-firmware/issues/3835)
**Author:** @5aji
**Created:** 2024-08-11T17:08:30Z
**Labels:** NFC, Bug

## Description

### Describe the bug.

Reading a DESFire card crashes the Flipper with a `furi_check()` error. It seems to crash after trying to read the second block. This is a card I had lying around, and I do not possess the keys (nor am I trying to get them). This happens on both 0.104.0 and 0.105.0-RC.

### Reproduction

1. Open NFC App -> Read
2. Alternatively, select Extra-> Read Specific -> DESFire
3. Touch Flipper to keycard
4. Lights blink for a split second and then the system reboots.

### Target

Mifare DESFire Card

### Logs

```Text
1050914 [D][NfcSupportedCards] Loaded 19 plugins
1050929 [D][Iso14443_4aPoller] Read ATS success
1050938 [D][MfDesfirePoller] Read version success
1050942 [D][MfDesfirePoller] Read free memory success
1050946 [D][MfDesfirePoller] Read master key settings success
1050950 [D][MfDesfirePoller] Read master key version success
1050955 [D][MfDesfirePoller] Read application ids success
1050958 [D][MfDesfirePoller] Selecting app 0
1050963 [D][MfDesfirePoller] Reading app 0
1050974 [D][MfDesfirePoller] Can't read file 0 data without authentication
1050978 [D][MfDesfirePoller] Selecting app 1
1050983 [D][MfDesfirePoller] Reading app 1
1050999 [D][MfDesfirePoller] Can't read file 1 data without authentication
1051002 [D][MfDesfirePoller] Selecting app 2
1051007 [D][MfDesfirePoller] Reading app 2

[CRASH][NfcWorker] furi_check failed
        r0 : 20025fe8
        r1 : 200251d0
        r2 : 0
        r3 : 0
        r4 : 0
        r5 : 0
        r6 : 20025fe8
        r7 : 200251d0
        r8 : 80a22e7
        r9 : 80a23d6
        r10 : 80a23e8
        r11 : 20031364
        lr : 80389d9
        stack watermark: 7556
             heap total: 186064
              heap free: 31576
         heap watermark: 27568
        core2: not faulted
Rebooting system�0
```


### Anything else?

I have a Proxmark3 if that would help provide more information. 

---
*This issue was automatically imported from the upstream Flipper Zero firmware repository.*
