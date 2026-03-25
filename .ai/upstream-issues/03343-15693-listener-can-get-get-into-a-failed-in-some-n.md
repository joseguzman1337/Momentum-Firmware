# Issue #3343: 15693 listener can get get into a failed in some noisy conditions and remain there until restart

**Original Issue:** [https://github.com/flipperdevices/flipperzero-firmware/issues/3343](https://github.com/flipperdevices/flipperzero-firmware/issues/3343)
**Author:** @nvx
**Created:** 2024-01-05T13:02:41Z
**Labels:** NFC, Bug

## Description

### Describe the bug.

While tracking down some bugs I suspect were introduced with the NFC refactor I discovered an interesting condition that can occur in the 15693 emulation code.

In `signal_reader_callback` in `iso15693_parser.c` when a SOF is recieved it then sets the expected demodulation mode to either 1or4 or 1or256 depending on what the SOF looked like. After this mode has been set remaining calls to the callback look for data encoded in that modulation only. The issue is that readers will generally only use one of the two modulations exclusively (for example picopass only supports the higher speed 1of4 mode) and there is no timeout that resets the state back to `Iso15693ParserStateParseSoF`, so under real world conditions sometimes a bit of noise can trigger the wrong mode at which point emulation will stop working until it is manually restarted as we never encounter the appropriate end of frame.

I'd expect that the demodulator would upon encountering invalid modulation reset the state back to `Iso15693ParserStateParseSoF` so that it can start from the beginning again.

### Reproduction

1. Attach debugger
2. Run picopass and emulate a credential
3. Read the credential a bunch of times from varying distances (note at some point you may run into flipperdevices/flipperzero-good-faps#105 as well)
4. When emulation stops working (everything looks fine on the FZ side of things, but the reader will not be able to see anything) add a breakpoint on the `signal_reader_callback` function
5. Observe that `instance->state` is `Iso15693ParserStateParseFrame` and `instance->mode` is `Iso15693ParserMode1OutOf256` which isn't used by picopass and that in all subsequent calls to this function the state and mode remains unchanged

### Target

_No response_

### Logs

_No response_

### Anything else?

_No response_

---
*This issue was automatically imported from the upstream Flipper Zero firmware repository.*
