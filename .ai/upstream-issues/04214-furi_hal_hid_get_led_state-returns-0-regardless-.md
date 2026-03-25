# Issue #4214: furi_hal_hid_get_led_state() returns 0 regardless of keyboard state

**Original Issue:** [https://github.com/flipperdevices/flipperzero-firmware/issues/4214](https://github.com/flipperdevices/flipperzero-firmware/issues/4214)
**Author:** @mantacid
**Created:** 2025-05-05T15:50:49Z
**Labels:** JS, Triage

## Description

### Describe the bug.

While trying to write a program that could obtain the status of the host device's lock keys, I noticed that the function that would allow me to do so (`furi_hal_hid_get_led_state`) would always return 0, regardless of the state of the hsot keyboard

### Reproduction

1. Load the attached javascript onto the flipper (github wouldn't let me upload the js file directly).
2. while the flipper is connected to a computer, run the script.
3. attempt to toggle the caps lock key during execution.

[bugtest copy.txt](https://github.com/user-attachments/files/20039694/bugtest.copy.txt)

### Target

_No response_

### Logs

```Text

```

### Anything else?

I'm running the momentum firmware, but have reason to believe that this is an issue on stock as well.

---
*This issue was automatically imported from the upstream Flipper Zero firmware repository.*
