# Issue #3282: NTAG216 Unlocking Issue

**Original Issue:** [https://github.com/flipperdevices/flipperzero-firmware/issues/3282](https://github.com/flipperdevices/flipperzero-firmware/issues/3282)
**Author:** @droidXrobot
**Created:** 2023-12-10T22:53:53Z
**Labels:** NFC

## Description

### Describe the bug.

I tried to unlock an NTAG216 by inputting a password manually. I got a success messaging saying all pages were unlocked successfully but when I tried to read the tag again it said "Password-protected pages!"

### Reproduction

1.  Navigate to NFC
2. Read a password protected NTAG216
3.  More
4. Unlock
5. Enter password manually
6. Save
7. Continue
8.  See message "All pages unlocked!"
9. Exit and read card again. It says  "Password-protected pages!"

### Target

 0.96.1

### Logs

_No response_

### Anything else?

 Flipper firmware 0.96.1

---
*This issue was automatically imported from the upstream Flipper Zero firmware repository.*
