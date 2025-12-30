# Issue #4269: Support non-standard Indala RFID fob

**Original Issue:** [https://github.com/flipperdevices/flipperzero-firmware/issues/4269](https://github.com/flipperdevices/flipperzero-firmware/issues/4269)
**Author:** @asportnoy
**Created:** 2025-08-28T03:23:48Z
**Labels:** RFID 125kHz, Triage

## Description

### Description of the feature you're suggesting.

I have an RFID keyfob that currently cannot be read by Flipper. I am >95% sure it is an Indala fob ([discussed in Discord](https://discord.com/channels/740930220399525928/954422698879098990/1408671165081325634) and that is the consensus) but I'm guessing it's a non-26 byte length since it doesn't seem to be supported. Beyond that, I don't know what byte length it actually is.

### Anything else?

Raw RFID dump: [Raw Data.zip](https://github.com/user-attachments/files/22016868/Raw.Data.zip) (had to zip it due to GH file type restrictions)

Happy to give any additional information if this is not sufficient.

Possibly related to #3046 or #1206

---
*This issue was automatically imported from the upstream Flipper Zero firmware repository.*
