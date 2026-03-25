# Issue #3618: FDI iPassan Mifare Plus emulation not working

**Original Issue:** [https://github.com/flipperdevices/flipperzero-firmware/issues/3618](https://github.com/flipperdevices/flipperzero-firmware/issues/3618)
**Author:** @Tomi2965
**Created:** 2024-04-26T15:08:33Z
**Labels:** NFC, Bug, Triage

## Description

### Describe the bug.

Emulation of original FDI Mifare Plus tokens on FDI iPassan reader not works. In log is only half of UID (see images). Token is marked as Mifare Classic 1k

![flpr-2024-04-26-17-00-12](https://github.com/flipperdevices/flipperzero-firmware/assets/152749132/80ab4abd-2cb8-47c1-b857-b41d1bb0ac50)
Code readed on Flipper

![Ipassan-1](https://github.com/flipperdevices/flipperzero-firmware/assets/152749132/3df6080a-ccec-4d0d-b305-1fb86eda30a6)
Yellow line - emulated via FZ, green line - token readed by reader. 

Note: please see, that FZ readed UID in reverse order. 

Token model: FDI GB-010-230
Reader model: FD-020-086

If anybody need any beta-test, or any info, do not hesitate and just ask! I have one iPassan at home for testing (including destructive tests). 

### Reproduction

Emulation of original FDI Mifare Plus token on FDI reader

### Target

_No response_

### Logs

_No response_

### Anything else?

Have a nice day! :) 

---
*This issue was automatically imported from the upstream Flipper Zero firmware repository.*
