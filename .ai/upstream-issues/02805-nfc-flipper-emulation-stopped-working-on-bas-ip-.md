# Issue #2805: [NFC] Flipper Emulation stopped working on BAS-IP BME-03 after enabling reader's security profile

**Original Issue:** [https://github.com/flipperdevices/flipperzero-firmware/issues/2805](https://github.com/flipperdevices/flipperzero-firmware/issues/2805)
**Author:** @mishamyte
**Created:** 2023-06-26T22:09:00Z
**Labels:** Feature Request, NFC

## Description

### Describe the bug.

There is an object with access system built on top of BAS-IP panels (BME-03 reader) + U-Prox readers (U-Prox SE mini + U-Prox SL mini). Mifare 1K tags were used. Initially the whole system worked only with tag UID. For that moment emulation of tag worked fine at all present readers.

Then the decision were taken to increase the security level. For that purposes new MFP tags were bought and all reader's settings were updated: added MFP profile and (what is important) MFC profile was added (for backward compatibility of all issued tags). 

The one key is used for all issued MFC tags, all sectors are protected by it (both A + B keys).  Reader tries to authenticate with that key for all sectors sequentially until auth will be successful.  Filter only against MF Zero is present.

After applying of those changes Flipper's emulation stopped working on the panels with BME-03 reader (and it is working on all other readers). All other tags (like MF-3, multiple versions of chinese CUID, Gen 4 GTU card) are working fine.

I made the dumps by Proxmark3, visually it looks like protocol executes fine. So I have a suggestion it could be a hardware error. 
But before that I decided to create that bug report for checking is it not a software problem. 

Thanks!

### Reproduction

1. Open saved tag (full decrypted with a know key, all sectors are read successfully)
2. Emulate it
3. Try to authenticate via panel with BAS-IP BME-03 reader

_Expected result:_
Door will be opened

_Actual result:_
Door is not opened

### Target

NFC

### Logs

Proxmark3 traces are attached:
[proxmark3-traces.zip](https://github.com/flipperdevices/flipperzero-firmware/files/11875049/proxmark3-traces.zip)

Original - original tag's trace
Flipper - Flipper's trace

### Anything else?

**Firmware version:** 0.85.2
_Dump file could be shared securely if needed_

CC @Astrrra prob?

---
*This issue was automatically imported from the upstream Flipper Zero firmware repository.*
