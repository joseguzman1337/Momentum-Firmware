# Issue #2104: Change USB Vendor ID and Product ID to something non generic

**Original Issue:** [https://github.com/flipperdevices/flipperzero-firmware/issues/2104](https://github.com/flipperdevices/flipperzero-firmware/issues/2104)
**Author:** @ikilledmypc
**Created:** 2022-12-08T08:55:50Z
**Labels:** Feature Request, Backlog, USB

## Description

### Describe the enhancement you're suggesting.

Currently the flipper device when connected to USB reports itself as a component id for the STM microcontroller and a generic USB device as product ID. Since snaps use this information to allow usage inside of snaps like Firefox. It's currently impossible to use the flipper for U2F on operating systems which use snaps like Ubuntu. 

It would be great if flippedevices would apply for their own vendor id / product id. So this issue can be resolved.

https://www.usb.org/getting-vendor-id

Related issue:
[Pull Request](https://github.com/snapcore/snapd/pull/12003)

### Anything else?

_No response_

---
*This issue was automatically imported from the upstream Flipper Zero firmware repository.*
