# Issue #4089: Bug in Manual Read: effects slix nfc, possibly others

**Original Issue:** [https://github.com/flipperdevices/flipperzero-firmware/issues/4089](https://github.com/flipperdevices/flipperzero-firmware/issues/4089)
**Author:** @FOSSBOSS
**Created:** 2025-01-31T01:59:02Z
**Labels:** NFC, Triage

## Description

### Describe the bug.

When you select a manual Read NFC if the slix tag is not found, the read process never times out.

### Reproduction

1.switch on.
2. navigate to NFC
3. read
4.Manual read
5. select slix nfc 
6. press read.
7. wait for the moon cycle to complete when your battery runs out. or re-flash your firmware. you can not escape the sequence, and it never times out. 

### Target

_No response_

### Logs

```Text

```

### Anything else?

_No response_

---
*This issue was automatically imported from the upstream Flipper Zero firmware repository.*
