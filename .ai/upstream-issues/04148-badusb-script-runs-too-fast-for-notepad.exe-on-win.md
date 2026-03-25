# Issue #4148: BadUSB script runs too fast for notepad.exe on Windows 11

**Original Issue:** [https://github.com/flipperdevices/flipperzero-firmware/issues/4148](https://github.com/flipperdevices/flipperzero-firmware/issues/4148)
**Author:** @ase1590
**Created:** 2025-03-12T19:40:43Z
**Labels:** Triage

## Description

### Describe the bug.

The current BadUSB STRING input speed the the Flipper provides in 1.2.0 by default exceed that which Windows can reliably keep up with. 

Running the Demo_Windows script will result in multiple missed characters, as will any script that has long amounts of string input.  

### Reproduction

1. run BadUSB
2. run the demo_windows.txt script 
3. note that the input is too fast, and characters are missed. 

### Target

1.2.0

Edit: this seems specific to Windows 11 and notepad.exe
see my comment [here](https://github.com/flipperdevices/flipperzero-firmware/issues/4148#issuecomment-2719719881)


---
*This issue was automatically imported from the upstream Flipper Zero firmware repository.*
