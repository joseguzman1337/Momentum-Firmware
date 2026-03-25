# Issue #2733: NexWatch/NexKey support added in .84 not working - will not read cards

**Original Issue:** [https://github.com/flipperdevices/flipperzero-firmware/issues/2733](https://github.com/flipperdevices/flipperzero-firmware/issues/2733)
**Author:** @i-am-mandalore
**Created:** 2023-06-05T13:48:32Z
**Labels:** RFID 125kHz, Bug

## Description

### Describe the bug.

Pull request 2680 (https://github.com/flipperdevices/flipperzero-firmware/pull/2680) was supposed to add support for NexWatch/NexKey, however with the new version installed I still cannot read cards.  I have tried both a NexWatch NexKey card, as well as a NexKey card from after Honeywell acquired them.  Neither works.  I can't seem to find the RFID read raw capability in the Flipper that I thought used to be there, but I'm adding scans of two keys from a Proxmark.  

I have also performed a full format of the SD card and factory reset of the device prior to reinstalling the firmware/databases and trying again.  No change.

NexWatch NexKey (physical card ID 86594567  6905):

[usb] pm3 --> lf search

[=] NOTE: some demods output possible binary
[=] if it finds something that looks like a tag
[=] False Positives ARE possible
[=]
[=] Checking for known tags...
[=]
[=] Inverted the demodulated data
[+]  NexWatch raw id : 0x40c00080
[+]     Magic number : 0x84
[+]         88bit id : 86594567 (0x05295407)
[+]             mode : 1
[=]  Raw : 560000000002424B1D10EF00

[+] Valid NexWatch ID found!

[=] Couldn't identify a chipset
[usb] pm3 --> data print
[+] DemodBuffer:
[+] 01010110000000000000000000000000
[+] 00000000000000100100001001001011
[+] 00011101000100001110111100000000
[+] 00000000000000000000000000000000

Honeywell NexKey (physical card ID 78782701  28009):

[usb] pm3 --> lf search

[=] NOTE: some demods output possible binary
[=] if it finds something that looks like a tag
[=] False Positives ARE possible
[=]
[=] Checking for known tags...
[=]
[=] Inverted the demodulated data
[+]  NexWatch raw id : 0x40c00080
[+]      fingerprint : Nexkey
[+]         88bit id : 78782701 (0x04b220ed)
[+]             mode : 1
[=]  Raw : 5600000000517419411B0D00

[+] Valid NexWatch ID found!

[=] Couldn't identify a chipset
[usb] pm3 --> data print
[+] DemodBuffer:
[+] 01010110000000000000000000000000
[+] 00000000010100010111010000011001
[+] 01000001000110110000110100000000
[+] 00000000000000000000000000000000

### Reproduction

1. Open 125kHz RFID app
2. Place Flipper over card
3. Select "Read"

### Target

_No response_

### Logs

_No response_

### Anything else?

_No response_

---
*This issue was automatically imported from the upstream Flipper Zero firmware repository.*
