# Issue #2385: MiZiP keys and card read support

**Original Issue:** [https://github.com/flipperdevices/flipperzero-firmware/issues/2385](https://github.com/flipperdevices/flipperzero-firmware/issues/2385)
**Author:** @LowSkillDeveloper
**Created:** 2023-02-11T20:22:32Z
**Labels:** Feature Request, NFC, RFID 125kHz

## Description

I have a "MiZiP" key for the coffee machine. As I understand it, they come in 2 types, NFC and RFID. And maybe they contain information about the balance on the key. But the flipper can't read the balance from these keys.
Or maybe they use a database on their side, . But even so, flipper cannot read the card id.

![MIZIP](https://user-images.githubusercontent.com/25121341/218278516-43397a4d-f52e-40a8-96e9-dcd3805be96d.jpg)


My flipper and phone does not see the NFC, so I can assume that the key is RFID.
When reading RFID with Flipper Zero, it gives this:

![Screenshot-20230211-205306](https://user-images.githubusercontent.com/25121341/218278492-de5cb420-1a22-490c-9544-1809774602e8.png)

> Filetype: Flipper RFID key
> Version: 1
> Key type: EM4100
> Data: 00 00 00 00 00


I also did "Read RAW RFID data" when the balance on the key was different. 88 coins, 82, 78, 66.
I don't know how and which program use to read RAW files, so I'll just attach them here:
https://github.com/LowSkillDeveloper/mizip-flipper-temp


Having a dump of the same key with different balances, I think it is possible to find a changing value if it is in the key. Or at least Flipper will be able to read the id of the key.

Also this is official site with information about MiZiP: https://newis.evocagroup.com/en/payment-solutions/mizip
Perhaps they also use specific NFC, so the flipper can't detect it?

### Anything else?

_No response_

---
*This issue was automatically imported from the upstream Flipper Zero firmware repository.*
