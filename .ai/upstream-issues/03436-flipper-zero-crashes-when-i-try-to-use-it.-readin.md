# Issue #3436: Flipper Zero Crashes when I try to use it. (Reading NFC, Saving IR Remote Sequences)

**Original Issue:** [https://github.com/flipperdevices/flipperzero-firmware/issues/3436](https://github.com/flipperdevices/flipperzero-firmware/issues/3436)
**Author:** @I-Am-Skoot
**Created:** 2024-02-09T14:28:08Z
**Labels:** NFC, Bug

## Description

### Describe the bug.

I had to replace a lost device.   Since then the new device has been consistently crashing.  This has been over the last 3 firmware versions, so I am inclined to believe it is a hardware issue, however the support team insisted I open a ticket here.



### Reproduction

1. Switch on the device
2.1. Open the NFC app
2.1 Read Card
2.2 Place flipper against card
2.3 Crash
2.2 Open cross remote app
2.3 Create a new sequence
2.4 start adding entries
2.5 Crash


### Target

_No response_

### Logs

```Text
_.-------.._                    -,
          .-""--..,,_/ /`-,               -,  \
       .:"          /:/  /'\  \     ,_...,  `. |  |
      /       ,----/:/  /`\ _\~`_-"`     _;
     '      / /`"""'\ \ \.~`_-'      ,-"'/
    |      | |  0    | | .-'      ,/`  /
   |    ,..\ \     ,.-"`       ,/`    /
  ;    :    `/`""\`           ,/--==,/-----,
  |    `-...|        -.___-Z:_______J...---;
  :         `                           _-'
 _L_  _     ___  ___  ___  ___  ____--"`___  _     ___
| __|| |   |_ _|| _ \| _ \| __|| _ \   / __|| |   |_ _|
| _| | |__  | | |  _/|  _/| _| |   /  | (__ | |__  | |
|_|  |____||___||_|  |_|  |___||_|_\   \___||____||___|

Welcome to Flipper Zero Command Line Interface!
Read Manual https://docs.flipperzero.one

Firmware version: 0.96.1 0.96.1 (5dbe1cf0 built on 08-12-2023)

>: log debug
Current log level: debug
Use <log ?> to list available log levels
Press CTRL+C to stop...
340848 [I][Loader] Loading /ext/apps/NFC/nfc.fap
340980 [I][Elf] Total size of loaded sections: 53013
340982 [I][Loader] Loaded in 134ms
340985 [I][AnimationManager] Unload animation 'L1_Waves_128x50'
342355 [D][NfcScanner] Found 5 base protocols
342363 [D][DolphinState] icounter 1, butthurt 0
342377 [D][Nfc] FWT Timeout
342404 [D][Nfc] FWT Timeout
342429 [D][Nfc] FWT Timeout
342481 [D][Nfc] FWT Timeout
342509 [D][Nfc] FWT Timeout
342532 [D][Nfc] FWT Timeout
342579 [D][Nfc] FWT Timeout
342604 [D][Nfc] FWT Timeout
342667 [D][Nfc] FWT Timeout
342695 [D][Nfc] FWT Timeout
342718 [D][Nfc] FWT Timeout
342743 [D][Nfc] FWT Timeout
342768 [D][Nfc] FWT Timeout
342820 [D][Nfc] FWT Timeout
342848 [D][Nfc] FWT Timeout
342871 [D][Nfc] FWT Timeout
342907 [D][Nfc] FWT Timeout
342932 [D][Nfc] FWT Timeout
342984 [D][Nfc] FWT Timeout
343012 [D][Nfc] FWT Timeout
343035 [D][Nfc] FWT Timeout
343060 [D][Nfc] FWT Timeout
343085 [D][Nfc] FWT Timeout
343137 [D][Nfc] FWT Timeout
343165 [D][Nfc] FWT Timeout
343188 [D][Nfc] FWT Timeout
343213 [D][Nfc] FWT Timeout
343238 [D][Nfc] FWT Timeout
343291 [D][Nfc] FWT Timeout
343319 [D][Nfc] FWT Timeout
343342 [D][Nfc] FWT Timeout
343367 [D][Nfc] FWT Timeout
343392 [D][Nfc] FWT Timeout
343444 [D][Nfc] FWT Timeout
343472 [D][Nfc] FWT Timeout
343495 [D][Nfc] FWT Timeout
343520 [D][Nfc] FWT Timeout
343545 [D][Nfc] FWT Timeout
343608 [D][Nfc] FWT Timeout
343638 [D][Nfc] FWT Timeout
343663 [D][Nfc] FWT Timeout
343688 [D][Nfc] FWT Timeout
343713 [D][Nfc] FWT Timeout
343765 [D][Nfc] FWT Timeout
343793 [D][Nfc] FWT Timeout
343816 [D][Nfc] FWT Timeout
343841 [D][Nfc] FWT Timeout
343866 [D][Nfc] FWT Timeout
343940 [D][Nfc] FWT Timeout
343968 [D][Nfc] FWT Timeout
343991 [D][Nfc] FWT Timeout
344016 [D][Nfc] FWT Timeout
344041 [D][Nfc] FWT Timeout
344093 [D][Nfc] FWT Timeout
344121 [D][Nfc] FWT Timeout
344180 [D][Nfc] FWT Timeout
344206 [D][Nfc] FWT Timeout
344269 [D][Nfc] FWT Timeout
344297 [D][Nfc] FWT Timeout
344312 [D][NfcScanner] Found 4 children
344369 [D][Nfc] FWT Timeout
344371 [D][Nfc] FWT Timeout
344405 [D][Nfc] FWT Timeout
344438 [D][Iso14443_4aPoller] Read ATS success
344470 [I][NfcScanner] Detected 1 protocols
344602 [D][Iso14443_4aPoller] Read ATS success
344612 [D][MfDesfirePoller] Read version success
344616 [D][MfDesfirePoller] Read free memory success
344620 [D][MfDesfirePoller] Read master key settings success
344625 [D][MfDesfirePoller] Read master key version success
344630 [D][MfDesfirePoller] Read application ids success
```


### Anything else?

I made a video of the issues

[![IMAGE ALT TEXT](http://img.youtube.com/vi/kWmxJfC7YiQ/0.jpg)](http://www.youtube.com/watch?v=kWmxJfC7YiQ "Flipper Crash")


---
*This issue was automatically imported from the upstream Flipper Zero firmware repository.*
