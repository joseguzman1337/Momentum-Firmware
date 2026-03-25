# Issue #4249: Reading NFC card while connected via USB to a computer and to qFlipper leads to a OOM Crash

**Original Issue:** [https://github.com/flipperdevices/flipperzero-firmware/issues/4249](https://github.com/flipperdevices/flipperzero-firmware/issues/4249)
**Author:** @hac-v
**Created:** 2025-07-11T18:02:28Z
**Labels:** NFC, Triage

## Description

### Describe the bug.

Firmware version 1.3.4.

$SUBJECT.

### Reproduction

1. Connect to a computer via USB cable;
2. Select "Read" to read an NFC card;
3. Observe the "out of memory" crash message before anything else appears on the screen.


The reproducer is reliable for me.

*[see log below]* ~~However, when I use the dev board to collect debug logs, the crash does not happen. I am not sure of the reason (I'm new to flipper, got mine two days ago). If there are better ways to collect this other than connecting the dev board to FlipperZero and via USB to a computer, let me know. ~~

### Target

_No response_

### Logs

Was able to reproduce by tapping buttons on the UI.

```Text
488376 [I][Elf] Total size of loaded sections: 888
488379 [D][Fap] Library for NfcSupportedCardPlugin, API v. 1 loaded
488426 [I][Elf] Total size of loaded sections: 420
488429 [D][Fap] Library for NfcSupportedCardPlugin, API v. 1 loaded
488449 [D][RpcGui] SendInputEvent
488459 [D][RpcGui] SendInputEvent
488498 [I][Elf] Total size of loaded sections: 1804
488501 [D][Fap] Library for NfcSupportedCardPlugin, API v. 1 loaded
488554 [I][Elf] Total size of loaded sections: 3212
488557 [D][Fap] Library for NfcSupportedCardPlugin, API v. 1 loaded
488622 [I][Elf] Total size of loaded sections: 4892
488625 [D][Fap] Library for NfcSupportedCardPlugin, API v. 1 loaded
488675 [I][Elf] Total size of loaded sections: 284
488678 [D][Fap] Library for NfcSupportedCardPlugin, API v. 1 loaded
488736 [I][Elf] Total size of loaded sections: 1356
488739 [D][Fap] Library for NfcSupportedCardPlugin, API v. 1 loaded
488779 [D][RpcGui] SendInputEvent
488793 [I][Elf] Total size of loaded sections: 820
488796 [D][Fap] Library for NfcSupportedCardPlugin, API v. 1 loaded
488856 [I][Elf] Total size of loaded sections: 1844
488860 [D][Fap] Library for NfcSupportedCardPlugin, API v. 1 loaded
488863 [D][RpcGui] SendInputEvent
488870 [D][RpcGui] SendInputEvent
488916 [I][Elf] Total size of loaded sections: 548
488919 [D][Fap] Library for NfcSupportedCardPlugin, API v. 1 loaded
488942 [D][RpcGui] SendInputEvent
488980 [I][Elf] Total size of loaded sections: 1396
488983 [D][Fap] Library for NfcSupportedCardPlugin, API v. 1 loaded
489029 [D][RpcGui] SendInputEvent
489046 [I][Elf] Total size of loaded sections: 1608
489049 [D][Fap] Library for NfcSupportedCardPlugin, API v. 1 loaded
489053 [D][RpcGui] SendInputEvent
489104 [I][Elf] Total size of loaded sections: 908
489107 [D][Fap] Library for NfcSupportedCardPlugin, API v. 1 loaded
489177 [I][Elf] Total size of loaded sections: 1212
489180 [D][Fap] Library for NfcSupportedCardPlugin, API v. 1 loaded
489196 [E][Elf] Not enough memory to load section data
489198 [E][Elf] Error loading section '.text'
489201 [E][Elf] Not enough memory
489215 [E][Elf] Not enough memory to load section data
489218 [E][Elf] Error loading section '.text'
489221 [E][Elf] Not enough memory
489235 [E][Elf] Not enough memory to load section data
489238 [E][Elf] Error loading section '.text'
489242 [E][Elf] Not enough memory
489301 [I][Elf] Total size of loaded sections: 1324
489304 [D][Fap] Library for NfcSupportedCardPlugin, API v. 1 loaded
489360 [I][Elf] Total size of loaded sections: 3276
489363 [D][Fap] Library for NfcSupportedCardPlugin, API v. 1 loaded
489416 [I][Elf] Total size of loaded sections: 1144
489419 [D][Fap] Library for NfcSupportedCardPlugin, API v. 1 loaded
489445 [E][Elf] Not enough memory to load section data
489448 [E][Elf] Error loading section '.text'
489451 [E][Elf] Not enough memory
489505 [I][Elf] Total size of loaded sections: 1956
489508 [D][Fap] Library for NfcSupportedCardPlugin, API v. 1 loaded
489560 [I][Elf] Total size of loaded sections: 368
489563 [D][Fap] Library for NfcSupportedCardPlugin, API v. 1 loaded
489618 [I][Elf] Total size of loaded sections: 1464
489621 [D][Fap] Library for NfcSupportedCardPlugin, API v. 1 loaded
489674 [I][Elf] Total size of loaded sections: 636
489677 [D][Fap] Library for NfcSupportedCardPlugin, API v. 1 loaded
489732 [I][Elf] Total size of loaded sections: 1024
489735 [D][Fap] Library for NfcSupportedCardPlugin, API v. 1 loaded
489740 [D][NfcSupportedCards] Loaded 22 plugins
489744 [D][ViewDispatcher] View changed while key press 20029BE8 -> 2002
489753 [D][MfClassicPoller] 4K detected

[CRASH][NfcWorker] out of memory
        r0 : 0
        r1 : 0
        r2 : 20000140
        r3 : 809f711
        r4 : 1040
        r5 : 0
        r6 : 0
        r7 : 1038
        r8 : a5a5a5a5
        r9 : 0
        r10 : 0
        r11 : 20031364
        lr : 801470b
        stack watermark: 7632
             heap total: 190144
              heap free: 8944
         heap watermark: 2952
        core2: not faulted
Rebooting system0 [I][FuriHalRtc] Init OK
```


---
*This issue was automatically imported from the upstream Flipper Zero firmware repository.*
