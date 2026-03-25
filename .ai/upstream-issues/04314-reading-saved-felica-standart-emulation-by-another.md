# Issue #4314: Reading saved Felica Standart emulation by another FZ leads to its crash

**Original Issue:** [https://github.com/flipperdevices/flipperzero-firmware/issues/4314](https://github.com/flipperdevices/flipperzero-firmware/issues/4314)
**Author:** @RebornedBrain
**Created:** 2025-12-01T08:57:40Z
**Labels:** None

## Description

### Describe the bug.

@zinongli There is a problem with new Felica Standard emulation/reading. See reproducion steps below. Issue happens here because system_total equals 0.

<img width="1545" height="1144" alt="Image" src="https://github.com/user-attachments/assets/624091b8-0d2f-43c8-a1f7-348c562ae83d" />

Looks like the roots of this issue are from doing load/save operations a little bit incorrectly. In those `felica_load` and `felica_save` functions there are bool flags `parsed` and `saved` respectively, which indicates the result of the operation. Newly added logic doesn't modify them. Let's take as an example `felica_load` function, there we have this check in red square which checks that everything before it was parsed fine, otherwise we exit with false. If everything is fine we continue and `parsed` is true, but what if we fail to read smth in code below? We also need to set that flag correctly.

<img width="1589" height="1167" alt="Image" src="https://github.com/user-attachments/assets/eb7d398b-667a-4401-9685-f5397d8f2152" />

And how issue happens, we start to read empy dump where there is no services for example, we reach this part and exit, but return parsed = true, while in fact we didn't complete reading and need to return false, for logic to work correctly.

<img width="1653" height="890" alt="Image" src="https://github.com/user-attachments/assets/f85f6251-fc41-4ddc-8a10-4d834945c738" />

Also I want to warn that fixing this issue by simply adding `parsed = false` to each break will not work (I've already tried 😿) because it will lead to another issue that completely fine blank Felica Standard cards will fail to open for emulation on FZ. 

Maybe some more checks about blank parts of Felica Standard could help, as an idea if we read count == 0, then we skip simple_array_init, or smth like that.



### Reproduction

1. You need two Flipper Zeros flashed with latest 1.4.2 release
2. Read empty Felica Standart card with one Flipper and save it.
3. Open new saved card and start emulation
4. Take another Flipper and try to read emulation.
Result: Flipper which performs reading crashes and reboot is needed to bring it back

### Target

1.4.2

### Logs

```Text
556561 [I][AnimationManager] Unload animation 'L2_Wake_up_128x64'
556575 [I][Loader] Loading /ext/apps/NFC/nfc.fap
556761 [I][Elf] Total size of loaded sections: 81253
556764 [I][Loader] Loaded in 189ms
574308 [I][NfcScanner] Detected 1 protocols
574417 [W][ViewPort] ViewPort lockup: see applications/services/gui/view_port.c:                           245
574483 [I][Elf] Total size of loaded sections: 9036
574530 [I][Elf] Total size of loaded sections: 888
574575 [I][Elf] Total size of loaded sections: 420
574625 [I][Elf] Total size of loaded sections: 2296
574675 [I][Elf] Total size of loaded sections: 1804
574742 [I][Elf] Total size of loaded sections: 3212
574804 [I][Elf] Total size of loaded sections: 4892
574851 [I][Elf] Total size of loaded sections: 284
574905 [I][Elf] Total size of loaded sections: 1356
574953 [I][Elf] Total size of loaded sections: 820
575003 [I][Elf] Total size of loaded sections: 1844
575056 [I][Elf] Total size of loaded sections: 548
575109 [I][Elf] Total size of loaded sections: 1396
575165 [I][Elf] Total size of loaded sections: 1608
575215 [I][Elf] Total size of loaded sections: 908
575273 [I][Elf] Total size of loaded sections: 1212
575330 [I][Elf] Total size of loaded sections: 5068
575392 [I][Elf] Total size of loaded sections: 4624
575449 [I][Elf] Total size of loaded sections: 4616
575500 [I][Elf] Total size of loaded sections: 1324
575553 [I][Elf] Total size of loaded sections: 3276
575604 [I][Elf] Total size of loaded sections: 1144
575682 [I][Elf] Total size of loaded sections: 9532
575752 [I][Elf] Total size of loaded sections: 1956
575802 [I][Elf] Total size of loaded sections: 368
575854 [I][Elf] Total size of loaded sections: 1464
575906 [I][Elf] Total size of loaded sections: 636
575959 [I][Elf] Total size of loaded sections: 1024
576006 [E][FelicaPoller] Request system code failed with error: 8

[CRASH][NfcWorker] furi_check failed
        r0 : 2000d2f8
        r1 : 0
        r2 : 20000140
        r3 : 2000d0d8
        r4 : 2000d2f8
        r5 : 0
        r6 : a5a5a5a5
        r7 : a5a5a5a5
        r8 : a5a5a5a5
        r9 : a5a5a5a5
        r10 : a5a5a5a5
        r11 : 20031364
        lr : 80378c9
        stack watermark: 7640
             heap total: 190144
              heap free: 42712
         heap watermark: 29624
        core2: not faulted
System halted. Connect debugger for more info
```

### Anything else?

_No response_

---
*This issue was automatically imported from the upstream Flipper Zero firmware repository.*
