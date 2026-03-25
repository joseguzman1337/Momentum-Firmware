# Issue #3756: Flipper crashes when continuously opening and closing the Passport screen

**Original Issue:** [https://github.com/flipperdevices/flipperzero-firmware/issues/3756](https://github.com/flipperdevices/flipperzero-firmware/issues/3756)
**Author:** @CookiePLMonster
**Created:** 2024-07-05T14:18:18Z
**Labels:** Bug, Core+Services

## Description

### Describe the bug.

When the user continuously presses DPad Right and Back buttons to spam opening and closing the Passport app, `furi_check` eventually triggers. I found it to be the easiest to reproduce on a Senpai animation.

### Reproduction

1. Press DPad Right.
2. Immediately press Back without giving the Passport app the chance to open.
3. Repeat until `furi_check` triggers.

### Target

_No response_

### Logs

```Text
25703 [I][Loader] App returned: 0
25704 [I][Loader] Application stopped. Free heap: 144896
26464 [I][AnimationManager] Select 'L1_Senpai_128x64' animation
26470 [I][AnimationManager] Load animation 'L1_Senpai_128x64'
26496 [I][SavedStruct] Loading "/int/.desktop.settings"
31916 [I][SavedStruct] Loading "/int/.desktop.settings"
31924 [I][Loader] Starting Passport
31926 [I][AnimationManager] Unload animation 'L1_Senpai_128x64'
32051 [D][GuiSrv] ViewPort changed while key press 2000A708 -> 20009370. Discarding key: Back, type: Short, sequence: 00000024
32057 [D][GuiSrv] ViewPort changed while key press 2000A708 -> 20009370. Sending key: Back, type: Release, sequence: 00000024 to previous view port
32427 [I][Loader] App returned: 0
32428 [I][Loader] Application stopped. Free heap: 144920
33202 [W][ViewPort] ViewPort lockup: see applications\services\gui\view_port.c:185
33205 [I][AnimationManager] Select 'L1_Senpai_128x64' animation
33209 [I][AnimationManager] Load animation 'L1_Senpai_128x64'
33214 [W][ViewPort] ViewPort lockup: see applications\services\gui\view_port.c:185
33217 [I][SavedStruct] Loading "/int/.desktop.settings"
33227 [I][SavedStruct] Loading "/int/.desktop.settings"
33245 [I][SavedStruct] Loading "/int/.desktop.settings"
33250 [I][Loader] Starting Passport
33266 [I][SavedStruct] Loading "/int/.desktop.settings"
33787 [W][ViewPort] ViewPort lockup: see applications\services\gui\view_port.c:185

[CRASH][LoaderSrv] furi_check failed
r0 : fffffffe
r1 : 0
r2 : 2000024c
r3 : 0
r4 : 20005838
r5 : 20011ee0
r6 : 20038f7c
r7 : 0
r8 : a5a5a5a5
r9 : a5a5a5a5
r10 : a5a5a5a5
r11 : 20031364
lr : 807754b
stack watermark: 1108
     heap total: 185536
      heap free: 118512
heap watermark: 89512
core2: not faulted
System halted. Connect debugger for more info
```


### Anything else?

The check is triggered with a `furi_semaphore_acquire` from `desktop_loader_callback` timing out. By adding additional logging I found out that when it crashes, `DesktopGlobalBeforeAppStarted` does not even begin processing, and therefore does not release the semaphore on time. My suspicion is that the view dispatcher queue, while not full (as `view_dispatcher_send_custom_event(desktop->view_dispatcher, DesktopGlobalBeforeAppStarted);` went through), is probably busy processing other kind of events and does not get to processing `DesktopGlobalBeforeAppStarted` in time.

Looking at the logs spamming `[I][SavedStruct] Loading "/int/.desktop.settings"` just before the crash, maybe the desktop reloads multiple times in those conditions? I also verified with additional logging that by the time it crashes, `DesktopGlobalAfterAppFinished` is **also** not being processed.

---
*This issue was automatically imported from the upstream Flipper Zero firmware repository.*
