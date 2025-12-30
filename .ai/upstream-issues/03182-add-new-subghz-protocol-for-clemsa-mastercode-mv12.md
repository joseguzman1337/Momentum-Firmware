# Issue #3182: Add new SubGhz protocol for Clemsa MasterCode MV12

**Original Issue:** [https://github.com/flipperdevices/flipperzero-firmware/issues/3182](https://github.com/flipperdevices/flipperzero-firmware/issues/3182)
**Author:** @flipperzelebro
**Created:** 2023-11-01T11:18:38Z
**Labels:** Feature Request, Sub-GHz

## Description

### Description of the feature you're suggesting.

I have a Clemsa Mastercode MV12 garage remote that its not supported now in flipper zero. 
Its a fixed code 433.92 MHz remote with modulation AM270.

Testing with flipperzero i have found that its very similar to Clemsa protocol already implemented, but with some changes:

- Time of the On, Off, pause.
- Length of the key.
- Order of the bits for switches.  

I attach the SUB files for te button 1 and button 2.
The DIP configuration is :
  
(+): ---**---
(o): --------
(-): \*\*\*--\*\*\*

I have already implemented the new protocol and could create a MR

[Mv12_B1.zip](https://github.com/flipperdevices/flipperzero-firmware/files/13226175/Mv12_B1.zip)

![617EPLOnN9L _AC_SL1024_](https://github.com/flipperdevices/flipperzero-firmware/assets/149575765/d9c464ca-e9dd-46fd-abee-26a1d5b00abb)

![mando-de-garaje-clemsa-mastercode-mv-12](https://github.com/flipperdevices/flipperzero-firmware/assets/149575765/3c2dd3c0-cbcb-442b-9cb8-a96e343233d4)



### Anything else?

I have already implemented the new protocol and could create a MR

---
*This issue was automatically imported from the upstream Flipper Zero firmware repository.*
