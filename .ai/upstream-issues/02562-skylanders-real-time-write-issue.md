# Issue #2562: Skylanders real-time write issue

**Original Issue:** [https://github.com/flipperdevices/flipperzero-firmware/issues/2562](https://github.com/flipperdevices/flipperzero-firmware/issues/2562)
**Author:** @Mikeonut
**Created:** 2023-04-04T04:35:11Z
**Labels:** NFC, Bug

## Description

### Describe the enhancement you're suggesting.

While Skylanders can work after being converted from .bin to .nfc files, they can only currently function on the Switch in a proper manner. In events which the portal would write to the tag, it will fail, unload the character, and re-set the figure to its original state. No progress can be made on the figure files. The portal writes to the figure when applying xp, gold, hats, upgrades, nicknames, basically everything you can do with an actual figure.

There needs to be a way to allow for these changes to be applied in real time so that issues like this in game do not occur, otherwise the only game that this device will work on is the Nintendo switch version of Imaginators. This issue also probably affects Disney Infinity figures as well.

### Anything else?

_No response_

---
*This issue was automatically imported from the upstream Flipper Zero firmware repository.*
