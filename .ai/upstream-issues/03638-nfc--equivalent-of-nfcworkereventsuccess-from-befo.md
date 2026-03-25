# Issue #3638: NFC: Equivalent of NfcWorkerEventSuccess from before NFC refactor

**Original Issue:** [https://github.com/flipperdevices/flipperzero-firmware/issues/3638](https://github.com/flipperdevices/flipperzero-firmware/issues/3638)
**Author:** @GMMan
**Created:** 2024-05-06T19:42:50Z
**Labels:** NFC, Triage

## Description

I'm finally getting around to updating my app that uses the old `NfcWorker` API to `NfcListener`, and I can't seem to find the equivalent of `NfcWorkerEventSuccess`. I was looking at `NfcEventTypeRxEnd` to add a hook for checking if something has changed, but it doesn't look like all events are propagated down to the callback fed to `nfc_listener_start()`. In particular, I'm using the Mifare Ultralight listener, and the only event it seems to propagate is `MfUltralightListenerEventTypeAuth`, which isn't very useful in my case. Is there some way I can detect that a write has occured to the emulated tag?

Also, just to confirm, when checking data I should be using `nfc_listener_get_data()` and commit back to the NFC device using `nfc_device_set_data()`? ~~Or does the architecture guarantee that I can just use `nfc_device_get_data()` directly (with the same protocol specified in `nfc_listener_alloc()`, of course)?~~ Just noticed its `NfcDevice` is internal, so I'll definitely have to do something different...

---
*This issue was automatically imported from the upstream Flipper Zero firmware repository.*
