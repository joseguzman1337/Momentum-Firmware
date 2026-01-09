# Issue #4012: Flipper Zero Mifare Plus 2K support (SL1 ONLY)

**Original Issue:** [https://github.com/flipperdevices/flipperzero-firmware/issues/4012](https://github.com/flipperdevices/flipperzero-firmware/issues/4012)
**Author:** @Overc1ocker
**Created:** 2024-11-22T10:18:45Z
**Labels:** Feature Request, NFC

## Description

### Description of the feature you're suggesting.

I know flipper has supported Mifare Classic 1K systems for awhile. This is mostly due to the insecure CRYPTO1 algorithm being used to secure the card. However, it seems that Mifare Plus systems are now slowly being used in place of Classic 1k and these are supposed to be encrypted with 128bit AES encryption. However, there is a catch. SL1 Mifare Plus systems are still using the insecure Crypto1 standard and currently Flipper zeros can read/ decrypt these SL1 cards in full by telling the Flipper they are actually Classic 1K (you may need to grab the keys using "detect reader"). The only problem with this is when doing some research online, I learned that certain SL1 cards make use of 2 additional partitions (16 and 17) and it doesn't seem as though the flipper can read these yet. Is it possible to add the extras in the future for experimentation purposes?

### Anything else?

_No response_

---
*This issue was automatically imported from the upstream Flipper Zero firmware repository.*
