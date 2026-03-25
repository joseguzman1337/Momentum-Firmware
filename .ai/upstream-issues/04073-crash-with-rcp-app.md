# Issue #4073: Crash with RCP app

**Original Issue:** [https://github.com/flipperdevices/flipperzero-firmware/issues/4073](https://github.com/flipperdevices/flipperzero-firmware/issues/4073)
**Author:** @gaellalire
**Created:** 2025-01-18T21:44:09Z
**Labels:** Bug, Core+Services

## Description

### Describe the bug.

When an RCP app is launched and not exited, the flipper crash with a fury message and pairing is lost.
You should close the app gracefully when connection is lost.
I tested with Sub-Ghz app but I guess it is for all RPC app.

Bluetooth connection is not reliable, you should manage lost connections properly.

### Reproduction

1) Launch an app in RPC mode in bluetooth (probably same issue with USB) with a phone
2) Disconnect (put the flipper in microwave for example)
3) Check that flipper crashed with an exception 

### Target

_No response_

### Logs

```Text

```

### Anything else?

_No response_

---
*This issue was automatically imported from the upstream Flipper Zero firmware repository.*
