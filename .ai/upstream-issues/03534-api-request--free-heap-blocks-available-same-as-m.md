# Issue #3534: API request: Free heap blocks available (same as memmgr_heap_printf_free_blocks)

**Original Issue:** [https://github.com/flipperdevices/flipperzero-firmware/issues/3534](https://github.com/flipperdevices/flipperzero-firmware/issues/3534)
**Author:** @noproto
**Created:** 2024-03-21T16:55:25Z
**Labels:** Feature Request, Core+Services

## Description

### Description of the feature you're suggesting.

Currently there's no way to check all of the available heap blocks of memory via the API.

It's not possible to plan heap allocation without repeatedly reserving memory and checking the next largest block with memmgr_heap_get_max_free_block (and if there's insufficient memory rolling back all of the allocations and re-allocating).

The only way I can see (which is a hack) is by setting up a log handler with furi_log_add_handler, call memmgr_heap_printf_free_blocks to dump the free blocks to the log buffered output stream, read back the log and parse each line, then use that in any heap memory planning function.

It would be very helpful to expose a function which can be used to plan help allocation/memory management in FAPs. If the largest sized block isn't checked, any malloc can fail freezing the device.

### Anything else?

_No response_

---
*This issue was automatically imported from the upstream Flipper Zero firmware repository.*
