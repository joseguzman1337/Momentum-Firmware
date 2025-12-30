# Issue #2465: Detect SL (sweden transport card) NFC

**Original Issue:** [https://github.com/flipperdevices/flipperzero-firmware/issues/2465](https://github.com/flipperdevices/flipperzero-firmware/issues/2465)
**Author:** @xSean145
**Created:** 2023-03-05T22:07:15Z
**Labels:** Feature Request, NFC

## Description

### Describe the enhancement you're suggesting.

Flipper Zero does not detect or read this card. Add support to detect and read this card.
Proxmark pulled this info from the card. (UID censored)

[usb] pm3 --> hf search
 🕕  Searching for ISO14443-A tag...          
[+]  UID: XX XX XX XX XX XX XX 
[+] ATQA: 00 44
[+]  SAK: 60 [1]
[+] MANUFACTURER: Infineon Technologies AG Germany
[=] -------------------------- ATS --------------------------
[+] ATS: 0B 78 80 74 03 80 54 05 30 3E 0F [ CF 00 ]
[=]      0B...............  TL    length is 11 bytes
[=]         78............  T0    TA1 is present, TB1 is present, TC1 is present, FSCI is 8 (FSC = 256)
[=]            80.........  TA1   different divisors are NOT supported, DR: [], DS: []
[=]               74......  TB1   SFGI = 4 (SFGT = 65536/fc), FWI = 7 (FWT = 524288/fc)
[=]                  03...  TC1   NAD is supported, CID is supported

[=] -------------------- Historical bytes --------------------
[+]   805405303E0F  (compact TLV data object)
[=]     54  05303E0F   Card issuer data

[?] Hint: try `hf mfu info`


[+] Valid ISO 14443-A tag found

[=] Short AID search:
[?] Hint: try emv commands

### Anything else?

It is recognized as a iso14443-4a.

---
*This issue was automatically imported from the upstream Flipper Zero firmware repository.*
