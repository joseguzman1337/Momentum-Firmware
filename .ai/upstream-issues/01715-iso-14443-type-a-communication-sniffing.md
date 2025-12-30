# Issue #1715: ISO 14443 Type A communication sniffing

**Original Issue:** [https://github.com/flipperdevices/flipperzero-firmware/issues/1715](https://github.com/flipperdevices/flipperzero-firmware/issues/1715)
**Author:** @koalazak
**Created:** 2022-09-07T14:56:17Z
**Labels:** Feature Request, NFC

## Description

### Description of the feature you're suggesting.

It would be great a new option to sniff the communication between reader and external tags to then show anti-col and authentication encrypted but relevant values: `uid, tag challenge, reader challenge, reader response, tag response`

Similar to `hf 14a snoop` + `hf list 14a` proxmark's commands.

I imagine this in two steps:

1. Actual sniff and save the data. 
    NFC > Extra Actions > Eavesdrop
    Message "Place Flipper and tag over the Reader..." and "REC" button on screen to start recording.
    Stop button appears and once clicked "save>" button appears. 
    Same behavior as "Read Raw" in sub-ghz menu. 

2. Select the dump and click on "Auth Info" to show the hex values for `uid, tag challenge, reader challenge, reader response and tag response` for all authentication flows in the dump.
     NFC > Saved > Dump1 > Auth Info
     Show the 5 relevant values on screen

![snoop_eng](https://user-images.githubusercontent.com/8185092/188903182-d7dd9026-5a27-43bf-8254-de31a3819ea7.jpeg)

With this values you can crack the keys externally without brute force them. What do you think?

### Anything else?

Is this currently available on FZ but inside another feature I missed? (I mean the sniff part)
Is the current FZ tag brutefoce attack based on dictionary or full scan?
Please let me know.

Thank you for your awesome work

---
*This issue was automatically imported from the upstream Flipper Zero firmware repository.*
