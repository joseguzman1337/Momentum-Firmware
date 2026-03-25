# Issue #4079: Export BLE buffers in SKD

**Original Issue:** [https://github.com/flipperdevices/flipperzero-firmware/issues/4079](https://github.com/flipperdevices/flipperzero-firmware/issues/4079)
**Author:** @loftyinclination
**Created:** 2025-01-24T16:16:16Z
**Labels:** Feature Request, Core+Services, Bluetooth

## Description

### Describe the enhancement you're suggesting.

When sending BLE HCI commands to the STM32WB55 coprocessor (using the process laid out in Annex 5289, 14.2.2) the command body must first be written into the `p_cmdBuffer`. Currently, it's not possible to write to this buffer in third party applications, since it's not referenced in the SDK, and so it's not possible to build any applications that use HCI commands.

(It is currently possible to listen for the responses to these events, via use of the `ble_event_dispatcher_register_svc_handler` function, which I think was included because the event handling is necessary for both ACI commands (which, as they don't require touching the `p_cmdBuffer`, are already callable from other applications), as well as HCI commands).

### Anything else?

_No response_

---
*This issue was automatically imported from the upstream Flipper Zero firmware repository.*
