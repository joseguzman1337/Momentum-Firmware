# Issue #4303: Freezing desktop animation

**Original Issue:** [https://github.com/flipperdevices/flipperzero-firmware/issues/4303](https://github.com/flipperdevices/flipperzero-firmware/issues/4303)
**Author:** @Crudefern
**Created:** 2025-10-30T03:07:55Z
**Labels:** None

## Description

### Describe the bug.

exactly what it says, the animation freezes on the first frame
doing things like opening and exiting an app un-freezes it but it will happen again if you repeat the steps
...the issue's so simple i'm not exactly sure what else to write other than it happens on 1.3.4, RC 1.4.0, and the latest commit (468cc45f)


### Reproduction

1. switch on
2. press left to open the apps menu
3. press back without launching anything

### Target

_No response_

### Logs

```Text
#sitting on the desktop after a reboot, about to press left
7959 [I][AnimationManager] Unload animation 'L1_Doom_128x64'
7976 [D][BrowserWorker] Start
7996 [D][BrowserWorker] Enter folder: /ext/apps items: 11 idx: -1
7998 [D][BrowserWorker] Load offset: 0 cnt: 50
9140 [D][BrowserWorker] End #this is the only line that appears when exiting the menu
```

### Anything else?

_No response_

---
*This issue was automatically imported from the upstream Flipper Zero firmware repository.*
