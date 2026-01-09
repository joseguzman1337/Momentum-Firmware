# Issue #3848: MIFARE Classic 1K EV1 is recognized as 1K, 16 sectors/32 keys

**Original Issue:** [https://github.com/flipperdevices/flipperzero-firmware/issues/3848](https://github.com/flipperdevices/flipperzero-firmware/issues/3848)
**Author:** @noproto
**Created:** 2024-08-20T00:09:12Z
**Labels:** NFC, Bug

## Description

### Describe the bug.

I have a MIFARE Classic 1K EV1 tag which I read with the Flipper and received this result:

![image](https://github.com/user-attachments/assets/9ca109cc-5fa4-421d-a381-bfce264d8b65)

Reading the same tag with the Proxmark results in:

```
[usb] pm3 --> hf mf autopwn
[=] MIFARE Classic EV1 card detected
(..)
[+] -----+-----+--------------+---+--------------+----
[+]  Sec | Blk | key A        |res| key B        |res
[+] -----+-----+--------------+---+--------------+----
[+]  000 | 003 | FFFFFFFFFFFF | D | FFFFFFFFFFFF | D
[+]  001 | 007 | 8A19D40CF2B5 | H | 8A19D40CF2B5 | R
[+]  002 | 011 | FFFFFFFFFFFF | D | FFFFFFFFFFFF | D
[+]  003 | 015 | FFFFFFFFFFFF | D | FFFFFFFFFFFF | D
[+]  004 | 019 | FFFFFFFFFFFF | D | FFFFFFFFFFFF | D
[+]  005 | 023 | FFFFFFFFFFFF | D | FFFFFFFFFFFF | D
[+]  006 | 027 | FFFFFFFFFFFF | D | FFFFFFFFFFFF | D
[+]  007 | 031 | FFFFFFFFFFFF | D | FFFFFFFFFFFF | D
[+]  008 | 035 | FFFFFFFFFFFF | D | FFFFFFFFFFFF | D
[+]  009 | 039 | FFFFFFFFFFFF | D | FFFFFFFFFFFF | D
[+]  010 | 043 | FFFFFFFFFFFF | D | FFFFFFFFFFFF | D
[+]  011 | 047 | FFFFFFFFFFFF | D | FFFFFFFFFFFF | D
[+]  012 | 051 | FFFFFFFFFFFF | D | FFFFFFFFFFFF | D
[+]  013 | 055 | FFFFFFFFFFFF | D | FFFFFFFFFFFF | D
[+]  014 | 059 | FFFFFFFFFFFF | D | FFFFFFFFFFFF | D
[+]  015 | 063 | 8A19D40CF2B5 | R | 8A19D40CF2B5 | R
[+]  016 | 067 | 5C8FF9990DA2 | D | D01AFEEB890A | D ( * )
[+]  017 | 071 | 75CCB59C9BED | D | 4B791BEA7BCC | D ( * )
[+] -----+-----+--------------+---+--------------+----
[=] ( * ) These sectors used for signature. Lays outside of user memory
```

Because `sectors_total` is miscalculated, this is interfering with the dictionary attack (which is not attempting to read the two signature sectors or discover these keys) and further may cause the card to fail emulation at a legitimate reader.

### Reproduction

Using an EV1 1K tag, read with official NFC app. Note 16 sectors and 32 keys tested.

### Target

12.F7B9C6 R02, OFW 0.105.0

### Logs

_No response_

### Anything else?

_No response_

---
*This issue was automatically imported from the upstream Flipper Zero firmware repository.*
