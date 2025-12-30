# Issue #2775: Mifare Plus golmar key is not emulated properly

**Original Issue:** [https://github.com/flipperdevices/flipperzero-firmware/issues/2775](https://github.com/flipperdevices/flipperzero-firmware/issues/2775)
**Author:** @mgrybyk
**Created:** 2023-06-13T23:23:45Z
**Labels:** NFC, Bug

## Description

### Describe the bug.

Emulation of golmar 13.56MHz tag that supports anti-copy encryption AES-128 doesn't work correctly.


### Reproduction

1. Read [golmar](https://www.golmar-seguridad.es/productos/tagdoor-mf-plus#product) key
2. Emulate it

**Actual Result**
the door won't open, the reader doesn't react anyhow.

**Expected Result**
the door should open

**Additional Info**
- my key [key.nfc.txt](https://github.com/flipperdevices/flipperzero-firmware/files/11729188/key.nfc.txt)
- I have 6 different readers, tried to use detect reader feature for all of them but still can see only sector 0. See [mfkey32.log](https://github.com/flipperdevices/flipperzero-firmware/files/11740128/mfkey32.log).
- the code written on the key is `80555B62663004`



### Target

_No response_

### Logs

```Text
Filetype: Flipper NFC keys
Version: 1
Mifare Classic type: 1K
Key A map: 000000000000FFFF
Key B map: 000000000000FFFF
Key A sector 0: 88 29 DA 9D AF 76
Key B sector 0: 88 29 DA 9D AF 76
```


### Anything else?

cc @Astrrra

---
*This issue was automatically imported from the upstream Flipper Zero firmware repository.*
