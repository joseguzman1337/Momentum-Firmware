# Issue #2386: Indala 224 card not being read

**Original Issue:** [https://github.com/flipperdevices/flipperzero-firmware/issues/2386](https://github.com/flipperdevices/flipperzero-firmware/issues/2386)
**Author:** @Divide-By-0
**Created:** 2023-02-12T00:43:05Z
**Labels:** Feature Request, RFID 125kHz

## Description

### Describe the bug.

I have a dual Indala 125 kHz ID and Mifare Classic 13.56 mHz card, and the Mifare classic reads fine on NFC. The Indala should read on the Extra Actions menu but nothing is detected.

### Reproduction

Switch to Indala mode
Try to read
It doesn't read

### Target

Indala card, len 224. Proxmark 3 recognizes it as chipset detection: EM4x05 / EM4x69.
The proxmark sometimes confueses it for a `COTAG Found: FC 240, CN: 64702 Raw: EBE3...`

### Logs

There's nothing shown on the screen, what command is most useful for me to put logs?

### Anything else?

I can read it on the Proxmark 3 (but not write it), it starts with 80000003...

---
*This issue was automatically imported from the upstream Flipper Zero firmware repository.*
