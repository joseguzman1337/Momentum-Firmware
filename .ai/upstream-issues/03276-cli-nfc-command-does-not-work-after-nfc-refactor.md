# Issue #3276: cli nfc command does not work after NFC refactor

**Original Issue:** [https://github.com/flipperdevices/flipperzero-firmware/issues/3276](https://github.com/flipperdevices/flipperzero-firmware/issues/3276)
**Author:** @u0d7i
**Created:** 2023-12-07T12:19:31Z
**Labels:** Feature Request, NFC

## Description

### Describe the bug.

After NFC refactor, cli "nfc" command shows empty sub-command list and does not work anymore:
```
+ device: /dev/ttyACM0
starting cli, Ctrl+C to terminate

              _.-------.._                    -,
          .-"```"--..,,_/ /`-,               -,  \ 
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

Firmware version: dev unknown (82baf1e9 built on 05-12-2023)

>: nfc
nfc
Usage:
nfc <cmd>
Cmd list:

>: 
```

### Reproduction

1. Connect to FZ serial port
2. Execute 'nfc' command via cli

### Target

7

### Logs

_No response_

### Anything else?

tested on latest devbuild ATM (latest releases and rc's have the same issues)

---
*This issue was automatically imported from the upstream Flipper Zero firmware repository.*
