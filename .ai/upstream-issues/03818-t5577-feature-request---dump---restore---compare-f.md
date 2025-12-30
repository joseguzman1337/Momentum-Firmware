# Issue #3818: T5577 Feature Request - dump / restore / compare feature

**Original Issue:** [https://github.com/flipperdevices/flipperzero-firmware/issues/3818](https://github.com/flipperdevices/flipperzero-firmware/issues/3818)
**Author:** @amalg
**Created:** 2024-07-31T17:28:40Z
**Labels:** Feature Request, RFID 125kHz

## Description

The low frequency T5577 chip is so versatile that even access control system manufacturers are using it over purchasing AWiD, EM, HID Prox, etc. LF chipsets, and replacement fob merchants are using them now too. Sometimes there are additional application data written to the T5577 and used by these systems than just their analog front-end configurations and ID data. This makes cloning the EM ID from a source T5577 to a fresh T5577 ineffective.

A good feature would be to be able to perform a complete memory dump of a T5577 chip to the Flipper Zero, then be able to write this complete memory dump to a new T5577. This would include block 0 config data and any additional application data, thus making it a perfect clone. Additionally, it would be really nice to be able to compare a dump file to a tag to check / ensure the write process has completed successfully.

---
*This issue was automatically imported from the upstream Flipper Zero firmware repository.*
