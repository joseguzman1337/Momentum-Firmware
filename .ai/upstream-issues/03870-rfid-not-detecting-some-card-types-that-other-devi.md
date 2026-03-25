# Issue #3870: RFID not detecting some card types that other devices detect (e.g. Keysy) 

**Original Issue:** [https://github.com/flipperdevices/flipperzero-firmware/issues/3870](https://github.com/flipperdevices/flipperzero-firmware/issues/3870)
**Author:** @PsiPhiTheta
**Created:** 2024-09-03T11:41:45Z
**Labels:** RFID 125kHz, Bug

## Description

### Describe the bug.

F0 is refusing to read some RFID cards (but working on others). I see a lot of posts about RFID functionality on the flipper being rather temperamental. I used to use the Keysy RFID cloner which works absolutely fine for everything I throw at it but I see some protocols seem to not have been programmed on flipper? Is that right? I will attach the raw reads to this issue for your reference. I also tried many times, completely still on a table, free from interference etc. 

### Reproduction

1. Switch on
2. Press RFID
3. Reading ASK / PSK scans continually without detecting anything 
[413psk.txt](https://github.com/user-attachments/files/16848016/413psk.txt)
[413ask.txt](https://github.com/user-attachments/files/16848017/413ask.txt)


### Target

Keysy rewritable key fob

### Logs

_No response_

### Anything else?

_No response_

---
*This issue was automatically imported from the upstream Flipper Zero firmware repository.*
