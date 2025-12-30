# Issue #1468: NFC Emulation of previously saved Mifare classic 1k card does not work.

**Original Issue:** [https://github.com/flipperdevices/flipperzero-firmware/issues/1468](https://github.com/flipperdevices/flipperzero-firmware/issues/1468)
**Author:** @bolmar3
**Created:** 2022-07-27T17:28:13Z
**Labels:** NFC, Bug

## Description

### Describe the bug.

I have multiple saved cards from 0.62.1, and in the latest release candidate, when I emulate the card, my phone cannot detect it at all. When I emulate a saved NTAG/Ultralight there is no issue.

### Reproduction

On 0.62, save a Mifare classic 1k card
Update to RC
NFC->Saved->saved card->Emulate
Phone cannot detect emulated card

### Target

e28446de49db99093c33dd43a1c4773d94e35942 (release-candidate)

### Logs

```Text
This is for a wifi tag I had: https://pastebin.com/R8s1gY2L

And this is for a contact (VCARD) mifare classic 1k card: https://pastebin.com/vA5HdcwK
```


### Anything else?

_No response_

---
*This issue was automatically imported from the upstream Flipper Zero firmware repository.*
