# Issue #3629: Custom crash/assert messages for FAPs

**Original Issue:** [https://github.com/flipperdevices/flipperzero-firmware/issues/3629](https://github.com/flipperdevices/flipperzero-firmware/issues/3629)
**Author:** @CookiePLMonster
**Created:** 2024-05-01T19:23:15Z
**Labels:** Core+Services

## Description

### Describe the enhancement you're suggesting.

# Description

The current implementations of `furi_check`, `furi_assert` and `furi_crash` allow the user to specify a custom crash message. This message is then displayed in serial logs, however, firmware-specified messages also come with an exclusive feature - [they are stored in the backup register and displayed on reboot](https://github.com/flipperdevices/flipperzero-firmware/blob/dev/furi/core/check.c#L166-L170). Only a pointer is preserved, which means that for obvious reasons, this cannot be done for errors resided in the FAP.

We've been brainstorming this with @Willy-JL and @kbembedded on Discord and came up with an idea that could use some more eyes on - because maybe it's reasonable, or maybe it's not viable and cannot be accepted. Either way, I'd be curious to hear an opinion about it.

The idea would be to repurpose a few more backup registers (STM32WB55 has [20](https://github.com/STMicroelectronics/cmsis_device_wb/blob/d1b860584dfe24d40d455ae624ed14600dfa93c9/Include/stm32wb55xx.h#L9338), Flipper currently uses 7) to store a short (12-16 characters) arbitrary error message, so it can display on screen regardless whether it comes from firmware or FAP.

# Example

A revised "crash flow" accepting arbitrary 16-character error messages would then go as follows:
1. Application calls `furi_crash("I crashed! Help!");`.
2. In `__furi_crash_implementation`, a pointer range check is done as usual. If the error string pointer resides inside a firmware or is one of the in-built magic check/assert messages, **set the top bit of that pointer**. This will act as a marker for `furi_hal_rtc_get_fault_data`, signaling that `FuriHalRtcRegisterFaultData` stores a pointer and not a C string.
3. If the string resides outside of the firmware, treat `FuriHalRtcRegisterFaultData`, `FuriHalRtcRegisterFaultData2`, `FuriHalRtcRegisterFaultData3` and `FuriHalRtcRegisterFaultData4` (added as part of this enhancement) as a `char[16]` buffer and `strncpy` the custom crash message into it. Since only ASCII is allowed, the top bit of `FuriHalRtcRegisterFaultData` remains cleared.
4. On reboot, `furi_hal_rtc_get_fault_data` checks the top bit and returns a pointer to the in-firmware error string, or a pointer to the arbitrary message stored in the 4 backup registers. This might require the message to be copied out to a local `static char[17]` or something similar.

# Benefits and risks

Pros:
1. Arbitrary messages can aid FAP debugging by the clever use of formatted messages - for example, one could devise a short assertion message with a line number and (part) of the filename.
2. FAPs can opt to show user-friendly crash messages for some critical points of failure.
3. No API version bump needed.

Cons:
1. Slightly increased code complexity.
2. Increased usage of the backup registers.

# Alternatives

If backup registers are out of the question, is there perhaps a different place to store the message in? A writable section of the flash that the firmware could `strncpy` the error message to? A file in the internal storage?

### Anything else?

_No response_

---
*This issue was automatically imported from the upstream Flipper Zero firmware repository.*
