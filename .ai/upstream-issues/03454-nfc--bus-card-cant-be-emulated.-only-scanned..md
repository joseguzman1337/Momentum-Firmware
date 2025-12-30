# Issue #3454: NFC: (Bus card) Cant be emulated. Only scanned.

**Original Issue:** [https://github.com/flipperdevices/flipperzero-firmware/issues/3454](https://github.com/flipperdevices/flipperzero-firmware/issues/3454)
**Author:** @Killer74-hub
**Created:** 2024-02-16T16:21:13Z
**Labels:** Feature Request, NFC

## Description


![Screenshot-20240216-175623](https://github.com/flipperdevices/flipperzero-firmware/assets/126610656/58514f04-9ddb-4e60-8acf-d1c7375a3b22)
![Screenshot-20240216-175616](https://github.com/flipperdevices/flipperzero-firmware/assets/126610656/baa86ea3-47a8-4ad2-b3bb-ab4de19b892b)
### Describe the bug.

The Card is this card: https://www.rmv.de/c/en/tickets/your-ticket/tickets-overview/annual-season-tickets

It is a german Bus ticket.

### Reproduction

1. Clone Card
2. Save the Card/Emulate Directly
3. Emulate the card

### Target

German Bus Card(NFC)

### Logs

```Text
Filetype: Flipper NFC device
Version: 4
# Device type can be ISO14443-3A, ISO14443-3B, ISO14443-4A, ISO14443-4B, ISO15693-3, FeliCa, NTAG/Ultralight, Mifare Classic, Mifare DESFire, SLIX, ST25TB
Device type: ISO14443-4A



scanned: 


72249131 [D][NfcScanner] Found 4 children
72249188 [D][Nfc] FWT Timeout
72249190 [D][Nfc] FWT Timeout
72249224 [D][Nfc] FWT Timeout
72249257 [D][Iso14443_4aPoller] Read ATS success
72249278 [I][NfcScanner] Detected 1 protocols
72249413 [D][Iso14443_4aPoller] Read ATS success
72249647 [D][DolphinState] icounter 555, butthurt 0


(I will give you the rest through discord if you need it. contact me.)
```


### Anything else?

Contact me through Discord if you want the NFC Card number/ more screenshots. I don´t want to give it to the public. 

discord: sniper74

---
*This issue was automatically imported from the upstream Flipper Zero firmware repository.*
