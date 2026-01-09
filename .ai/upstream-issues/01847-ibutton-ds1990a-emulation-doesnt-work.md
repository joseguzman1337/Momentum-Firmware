# Issue #1847: iButton ds1990a emulation doesn't work

**Original Issue:** [https://github.com/flipperdevices/flipperzero-firmware/issues/1847](https://github.com/flipperdevices/flipperzero-firmware/issues/1847)
**Author:** @jagotu
**Created:** 2022-10-07T22:09:00Z
**Labels:** Bug, iButton

## Description

### Describe the bug.

I've been having issues with emulating my iButton to the door lock, so I took a logic analyzer to it and got some recordings.

It seems to me (and I'm an amateur at this) like the window between resets left by the reader is just 230 microseconds and the flipper doesn't react fast enough.

This is what the emulation attempt looks like:
![image](https://user-images.githubusercontent.com/2465633/194669046-1a928074-f868-40fa-ae8a-d9d99fb1405e.png)

Between resets, there's just 230 microseconds:
![image](https://user-images.githubusercontent.com/2465633/194669522-68e5d39f-4416-4e19-b6bc-7ea326cfaac1.png)

I also MITM'd the actual key and it reacts with the presence signal in 35 microseconds:
![image](https://user-images.githubusercontent.com/2465633/194669109-893ae21f-3115-4b65-acb8-6362fb8ca3cf.png)

I also attach saleae recordings of the failed emulation attempt and what a succesful communication looks like. The MITM communaction is cut-off before the UID transmission but the beginning of the transaction is clearly visible.

[1wire_saleae.zip](https://github.com/flipperdevices/flipperzero-firmware/files/9737690/1wire_saleae.zip)

I have pretty much unlimited access to the button, the readers and the logic analyzer, so I can provide more captures if necessary.


### Reproduction

1. Emulate a ds1990a iButton
2. Attach Flipper to the reader, making sure there is good connectivity.
3. No reaction whatsoever from the reader.

### Target

_No response_

### Logs

_No response_

### Anything else?

_No response_

---
*This issue was automatically imported from the upstream Flipper Zero firmware repository.*
