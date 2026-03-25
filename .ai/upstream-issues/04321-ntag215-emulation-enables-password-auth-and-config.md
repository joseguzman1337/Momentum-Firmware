# Issue #4321: NTAG215 emulation enables password auth and config lock too early

**Original Issue:** [https://github.com/flipperdevices/flipperzero-firmware/issues/4321](https://github.com/flipperdevices/flipperzero-firmware/issues/4321)
**Author:** @Firefox2100
**Created:** 2025-12-25T14:25:16Z
**Labels:** None

## Description

### Describe the bug.

In a proper NTAG215 tag, when it first shipped with AUTH0 not configured and the write start, it's in `ACTIVE` state, and all pages are not protected. Later once the password and AUTH0 is written into, without an explict HLTA or power cycle, the tag stays in `ACTIVE` state and does not require password to write to protected pages. See below in the logs for a trace of mobile application Ally performing write on an NTAG215.

After writing the block 134 and 133, AUTH0 is set to protect anything beyond block 4 with write to 131, then with no PWD-AUTH, the write to 132 succeeded, showing that the tag does not immediately require authentication when AUTH0 is configured within the same session.

However on Flipper Zero, this is immediate -- password auth is required immediately after writing to 131, causing the next write to 132 to NAK without PWD-AUTH. This creates a discrepency between real NTAG215 and Flipper emulation. Similarly, the CFGLCK is also enabled immediately after writing, while the datasheet explictly states that the CFGLCK will only be enabled after a power cycle.

### Reproduction

1. Load an NFC file for an empty NTAG215
2. Enable emulation
3. Trying to write into it with a tool that does the aforementioned sequence, for example TagMo or Ally
4. Tool returns an error. Sniffing with PM3 confirms that the write to page 132 gets NAK. Going through the code there's no delayed activation of password auth or CFGLCK.

### Target

NFC emulation

### Logs

```Text
Ally writing to NTAG215


      Start |        End | Src | Data (! denotes parity error)                                           | CRC | Annotation
------------+------------+-----+-------------------------------------------------------------------------+-----+--------------------
          0 |       1056 | Rdr |26(7)                                                                    |     | REQA
       2244 |       4612 | Tag |44  00                                                                   |     | 
      11776 |      16544 | Rdr |50  00  57  cd                                                           |  ok | HALT
      39072 |      40064 | Rdr |52(7)                                                                    |     | WUPA
      41316 |      43684 | Tag |44  00                                                                   |     | 
      50848 |      53312 | Rdr |93  20                                                                   |     | ANTICOLL
      54500 |      60324 | Tag |88  04  e2  0b  65                                                       |     | 
      67504 |      77968 | Rdr |93  70  88  04  e2  0b  65  1f  17                                       |  ok | SELECT_UID
      79220 |      82740 | Tag |04  da  17                                                               |     | 
      89904 |      92368 | Rdr |95  20                                                                   |     | ANTICOLL-2
      93556 |      99444 | Tag |66  10  02  89  fd                                                       |     | 
     106560 |     117088 | Rdr |95  70  66  10  02  89  fd  dd  1a                                       |  ok | SELECT_UID-2
     118276 |     121860 | Tag |00  fe  51                                                               |     | 
     264976 |     268592 | Rdr |60  f8  32                                                               |  ok | EV1 VERSION
     269780 |     281428 | Tag |00  04  04  02  01  00  11  03  01  9e                                   |  ok | 
     328544 |     333312 | Rdr |50  00  57  cd                                                           |  ok | HALT
     473920 |     474912 | Rdr |52(7)                                                                    |     | WUPA
     476164 |     478532 | Tag |44  00                                                                   |     | 
     485696 |     496160 | Rdr |93  70  88  04  e2  0b  65  1f  17                                       |  ok | SELECT_UID
     497412 |     500932 | Tag |04  da  17                                                               |     | 
     508112 |     518640 | Rdr |95  70  66  10  02  89  fd  dd  1a                                       |  ok | SELECT_UID-2
     519828 |     523412 | Tag |00  fe  51                                                               |     | 
     617488 |     621104 | Rdr |55  d6  54                                                               |  ok | 
    5804160 |    5805216 | Rdr |26(7)                                                                    |     | REQA
    5806404 |    5808772 | Tag |44  00                                                                   |     | 
    5815936 |    5820704 | Rdr |50  00  57  cd                                                           |  ok | HALT
    5843232 |    5844224 | Rdr |52(7)                                                                    |     | WUPA
    5845476 |    5847844 | Tag |44  00                                                                   |     | 
    5855008 |    5857472 | Rdr |93  20                                                                   |     | ANTICOLL
    5858660 |    5864484 | Tag |88  04  e2  0b  65                                                       |     | 
    5871664 |    5882128 | Rdr |93  70  88  04  e2  0b  65  1f  17                                       |  ok | SELECT_UID
    5883380 |    5886900 | Tag |04  da  17                                                               |     | 
    5894064 |    5896528 | Rdr |95  20                                                                   |     | ANTICOLL-2
    5897716 |    5903604 | Tag |66  10  02  89  fd                                                       |     | 
    5910720 |    5921248 | Rdr |95  70  66  10  02  89  fd  dd  1a                                       |  ok | SELECT_UID-2
    5922436 |    5926020 | Tag |00  fe  51                                                               |     | 
    5981008 |    5984624 | Rdr |60  f8  32                                                               |  ok | EV1 VERSION
    5985812 |    5997460 | Tag |00  04  04  02  01  00  11  03  01  9e                                   |  ok | 
    6045760 |    6050528 | Rdr |50  00  57  cd                                                           |  ok | HALT
    6140912 |    6141904 | Rdr |52(7)                                                                    |     | WUPA
    6143156 |    6145524 | Tag |44  00                                                                   |     | 
    6152704 |    6163168 | Rdr |93  70  88  04  e2  0b  65  1f  17                                       |  ok | SELECT_UID
    6164420 |    6167940 | Tag |04  da  17                                                               |     | 
    6175104 |    6185632 | Rdr |95  70  66  10  02  89  fd  dd  1a                                       |  ok | SELECT_UID-2
    6186820 |    6190404 | Tag |00  fe  51                                                               |     | 
    6249920 |    6253536 | Rdr |60  f8  32                                                               |  ok | EV1 VERSION
    6254724 |    6266372 | Tag |00  04  04  02  01  00  11  03  01  9e                                   |  ok | 
    6331984 |    6336752 | Rdr |3c  00  a2  01                                                           |  ok | READ SIG
    6337940 |    6377236 | Tag |00  00  00  00  00  00  00  00  00  00  00  00  00  00  00  00  00  00   |     | 
            |            |     |00  00  00  00  00  00  00  00  00  00  00  00  00  00  20  da           |  ok | 
    6437840 |    6443760 | Rdr |3a  00  03  5b  62                                                       |  ok | READ RANGE (0-3)
    6444948 |    6465812 | Tag |04  e2  0b  65  66  10  02  89  fd  48  00  00  e1  10  3e  00  e6  f4   |  ok | 
    6536464 |    6540080 | Rdr |60  f8  32                                                               |  ok | EV1 VERSION
    6541268 |    6552916 | Tag |00  04  04  02  01  00  11  03  01  9e                                   |  ok | 
    6615104 |    6619872 | Rdr |3c  00  a2  01                                                           |  ok | READ SIG
    6621060 |    6660356 | Tag |00  00  00  00  00  00  00  00  00  00  00  00  00  00  00  00  00  00   |     | 
            |            |     |00  00  00  00  00  00  00  00  00  00  00  00  00  00  20  da           |  ok | 
    6732768 |    6742080 | Rdr |a2  04  a5  00  0a  00  2d  a3                                           |  ok | WRITEBLOCK(4)
    6795172 |    6795748 | Tag |0a(3)                                                                    |     | 
    6860400 |    6869712 | Rdr |a2  05  a8  e1  08  b7  1f  82                                           |  ok | WRITEBLOCK(5)
    6922804 |    6923380 | Tag |0a(3)                                                                    |     | 
    6988320 |    6997632 | Rdr |a2  06  c8  da  08  49  ce  b7                                           |  ok | WRITEBLOCK(6)
    7050724 |    7051300 | Tag |0a(3)                                                                    |     | 
...
   22456352 |   22465664 | Rdr |a2  80  da  7a  5e  3a  38  35                                           |  ok | WRITEBLOCK(128) (?)
   22518756 |   22519332 | Tag |0a(3)                                                                    |     | 
   22586224 |   22595600 | Rdr |a2  81  5c  da  e4  1e  67  f7                                           |  ok | WRITEBLOCK(129) (?)
   22648628 |   22649204 | Tag |0a(3)                                                                    |     | 
   22711312 |   22720688 | Rdr |a2  86  80  80  00  00  68  2f                                           |  ok | WRITEBLOCK(134) (?)
   22773716 |   22774292 | Tag |0a(3)                                                                    |     | 
   22840480 |   22849792 | Rdr |a2  85  2e  4e  ce  cc  80  78                                           |  ok | WRITEBLOCK(133) (?)
   22902884 |   22903460 | Tag |0a(3)                                                                    |     | 
   22964432 |   22973744 | Rdr |a2  03  f1  10  ff  ee  5e  bd                                           |  ok | WRITEBLOCK(3)
   23026836 |   23027412 | Tag |0a(3)                                                                    |     | 
   23093488 |   23102864 | Rdr |a2  83  00  00  00  04  9a  6e                                           |  ok | WRITEBLOCK(131) (?)
   23155892 |   23156468 | Tag |0a(3)                                                                    |     | 
   23222160 |   23231536 | Rdr |a2  84  5f  00  00  00  8d  7f                                           |  ok | WRITEBLOCK(132) (?)
   23284564 |   23285140 | Tag |0a(3)                                                                    |     | 
   23348512 |   23357824 | Rdr |a2  82  01  00  0f  bd  e7  d2                                           |  ok | WRITEBLOCK(130) (?)
   23410916 |   23411492 | Tag |0a(3)                                                                    |     | 
   23475344 |   23484720 | Rdr |a2  02  fd  48  0f  e0  79  f1                                           |  ok | WRITEBLOCK(2)
   23537748 |   23538324 | Tag |0a(3)                                                                    |     | 
   23605248 |   23610016 | Rdr |50  00  57  cd                                                           |  ok | HALT
   63458960 |   63460016 | Rdr |26(7)                                                                    |     | REQA
   63461204 |   63463572 | Tag |44  00                                                                   |     | 
   63470736 |   63475504 | Rdr |50  00  57  cd                                                           |  ok | HALT
   63498032 |   63499024 | Rdr |52(7)                                                                    |     | WUPA
   63500276 |   63502644 | Tag |44  00                                                                   |     | 
   63509808 |   63512272 | Rdr |93  20                                                                   |     | ANTICOLL
   63513476 |   63519300 | Tag |88  04  e2  0b  65                                                       |     | 
   63526464 |   63536928 | Rdr |93  70  88  04  e2  0b  65  1f  17                                       |  ok | SELECT_UID
   63538180 |   63541700 | Tag |04  da  17                                                               |     | 
   63548864 |   63551328 | Rdr |95  20                                                                   |     | ANTICOLL-2
   63552532 |   63558420 | Tag |66  10  02  89  fd                                                       |     | 
   63565520 |   63576048 | Rdr |95  70  66  10  02  89  fd  dd  1a                                       |  ok | SELECT_UID-2
   63577236 |   63580820 | Tag |00  fe  51                                                               |     | 
   63663280 |   63667984 | Rdr |30  02  10  8b                                                           |  ok | READBLOCK(2)
   63721092 |   63741956 | Tag |fd  48  0f  e0  f1  10  ff  ee  a5  00  0a  00  a8  e1  08  b7  4f  67   |  ok | 
   63937632 |   63938688 | Rdr |26(7)                                                                    |     | REQA
   63939876 |   63942244 | Tag |44  00                                                                   |     | 
   63949408 |   63954176 | Rdr |50  00  57  cd                                                           |  ok | HALT
```

### Anything else?

_No response_

---
*This issue was automatically imported from the upstream Flipper Zero firmware repository.*
