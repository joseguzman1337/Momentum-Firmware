# Issue #2898: Buttons for ONN brand ROKU TVs 

**Original Issue:** [https://github.com/flipperdevices/flipperzero-firmware/issues/2898](https://github.com/flipperdevices/flipperzero-firmware/issues/2898)
**Author:** @fennectech
**Created:** 2023-07-19T04:50:57Z
**Labels:** Feature Request, Infrared

## Description

### Describe the enhancement you're suggesting.

I’d like to see these added to the universal remote library
```
Version: 1
# 
name: Vol -
type: parsed
protocol: NECext
address: EA C7 00 00
command: 10 EF 00 00
# 
name: Vol +
type: parsed
protocol: NECext
address: EA C7 00 00
command: 0F F0 00 00
# 
name: Mute
type: parsed
protocol: NECext
address: EA C7 00 00
command: 20 DF 00 00
# 
name: Power
type: parsed
protocol: NECext
address: EA C7 00 00
command: 17 E8 00 00
```

### Anything else?

_No response_

---
*This issue was automatically imported from the upstream Flipper Zero firmware repository.*
