# Issue #2864: NFC: CP-Z-2 (mod. MF-I) can't do anti-collision with Flipper Zero emulation

**Original Issue:** [https://github.com/flipperdevices/flipperzero-firmware/issues/2864](https://github.com/flipperdevices/flipperzero-firmware/issues/2864)
**Author:** @AloneLiberty
**Created:** 2023-07-11T21:59:24Z
**Labels:** NFC, Bug

## Description

### Describe the bug.

To the ongoing problems with this reader (four-line version). I honestly don't know whose problem this is: reader works fine with fob and pm3 emulation, very bad with regular cards (pm3 sniffing making it even worse) and not working with Flipper Zero at all. Reader is UID only mode, no filters, reading gen1 fine.
From Flipper Zero emulation trace I see it doesn't go any further after REQ (flipper_emulation.trace):

```
  213669024 |  213670080 | Rdr |26(7)                                                                    |     | REQA
  213670080 |  213671268 |     |fdt (Frame Delay Time): 1188
  213671268 |  213673636 | Tag |44  00                                                                   |     | 
  215348512 |  215349568 | Rdr |26(7)                                                                    |     | REQA
  215349568 |  215350756 |     |fdt (Frame Delay Time): 1188
  215350756 |  215353124 | Tag |44  00                                                                   |     | 
  217030020 |  217032388 | Tag |44  00                                                                   |     | 
  218706992 |  218708048 | Rdr |26(7)                                                                    |     | REQA
  218708048 |  218709236 |     |fdt (Frame Delay Time): 1188
  218709236 |  218711604 | Tag |44  00                                                                   |     | 
  220386416 |  220387472 | Rdr |26(7)                                                                    |     | REQA
  220387472 |  220388660 |     |fdt (Frame Delay Time): 1188
  220388660 |  220391028 | Tag |44  00                                                                   |     | 
  222065824 |  222066880 | Rdr |26(7)                                                                    |     | REQA
  222066880 |  222068068 |     |fdt (Frame Delay Time): 1188
  222068068 |  222070436 | Tag |44  00                                                                   |     | 
  223744976 |  223746032 | Rdr |26(7)                                                                    |     | REQA
  223746032 |  223747220 |     |fdt (Frame Delay Time): 1188
  223747220 |  223749588 | Tag |44  00                                                                   |     | 
```

As suggested in community, placing tag before Flipper affects it, reader selects tag UID, not Flipper. We can't move reader into secure mode (MFC reading) yet. But from this side, it is clear why Detect reader works in this case (tag UID == Flipper emulation UID)(flipper_fob_stack_emulation.trace):

```
  102553392 |  102554448 | Rdr |26(7)                                                                    |     | REQA
  102554448 |  102555636 |     |fdt (Frame Delay Time): 1188
  102555636 |  102556532 | Tag |04(6)                                                                    |     | 
  102560160 |  102562624 | Rdr |93  20                                                                   |     | ANTICOLL
  102562624 |  102563812 |     |fdt (Frame Delay Time): 1188
  102563812 |  102564196 | Tag |00(2)                                                                    |     | 
  102574800 |  102585328 | Rdr |93  70  00  56  78  bb  95  e8  1c                                       |  ok | SELECT_UID
  106663872 |  106664928 | Rdr |26(7)                                                                    |     | REQA
  106664928 |  106666116 |     |fdt (Frame Delay Time): 1188
  106666116 |  106667268 | Tag |04                                                                       |     | 
  106670640 |  106673104 | Rdr |93  20                                                                   |     | ANTICOLL
  106673104 |  106674292 |     |fdt (Frame Delay Time): 1188
  106674292 |  106674676 | Tag |00(2)                                                                    |     | 
  106685280 |  106695808 | Rdr |93  70  00  56  78  bb  95  e8  1c                                       |  ok | SELECT_UID
  108376880 |  108377936 | Rdr |26(7)                                                                    |     | REQA
  108377936 |  108379108 |     |fdt (Frame Delay Time): 1172
  108379108 |  108381476 | Tag |44  00                                                                   |     | 
  108383648 |  108386112 | Rdr |93  20                                                                   |     | ANTICOLL
  108386112 |  108387284 |     |fdt (Frame Delay Time): 1172
  108387284 |  108392980 | Tag |04! d6! 35  f7! 97                                                       |     | 
  108398288 |  108408816 | Rdr |93  70  00  56  78  bb  95  e8  1c                                       |  ok | SELECT_UID
  110088896 |  110089952 | Rdr |26(7)                                                                    |     | REQA
  110089952 |  110091140 |     |fdt (Frame Delay Time): 1188
  110091140 |  110093508 | Tag |44  00                                                                   |     | 
  110095664 |  110098128 | Rdr |93  20                                                                   |     | ANTICOLL
  110098128 |  110099316 |     |fdt (Frame Delay Time): 1188
  110099316 |  110105140 | Tag |04! d6! 3d! ff! 97!                                                      |     | 
  110110304 |  110120832 | Rdr |93  70  00  56  78  bb  95  e8  1c                                       |  ok | SELECT_UID
  111800976 |  111802032 | Rdr |26(7)                                                                    |     | REQA
  111802032 |  111803220 |     |fdt (Frame Delay Time): 1188
  111803220 |  111804116 | Tag |04(6)                                                                    |     | 
  111807744 |  111810208 | Rdr |93  20                                                                   |     | ANTICOLL
  111810208 |  111811396 |     |fdt (Frame Delay Time): 1188
  111811396 |  111811780 | Tag |00(2)                                                                    |     | 
  113492656 |  113493712 | Rdr |26(7)                                                                    |     | REQA
```

From our tests we seen Flipper Zero 2 times sending UID properly, but we couldn't replicate how we done it. NFC refactor branch doesn't change anything (tried UID emulation). Messing with st25r3916 registers also didn't change anything.

Traces:
[traces.zip](https://github.com/flipperdevices/flipperzero-firmware/files/12021690/traces.zip)

Regardless naming:
`fob.trace` - regular gen1 fob, working great
`card.trace` - regular gen1 card, working once in a while
`flipper_emulation.trace` - Flipper Zero emulation, doesn't work
`flipper_fob_stack.trace` - Flipper Zero emulation + fob at back
`hf_sniff.pm3` - `hf sniff` on reader
`hf_sniff_flipper.pm3` and `hf_sniff_flipper_two.pm3` - `hf sniff` on reader + Flipper Zero emulation
`hf_sniff_fob.pm3` - `hf sniff` on reader + fob


### Reproduction

1. Emulate UID/MFC (doesn't matter) 
2. Try to scan with CP-Z-2

### Target

_No response_

### Logs

_No response_

### Anything else?

@g3gg0 (_as emulation expert_) maybe you could suggest something? 
Anti-collision preforms on ST25R3916 directly and _different frequency_ issue can't affect it?

---
*This issue was automatically imported from the upstream Flipper Zero firmware repository.*
