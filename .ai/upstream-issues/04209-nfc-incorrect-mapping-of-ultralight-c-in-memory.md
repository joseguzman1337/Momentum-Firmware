# Issue #4209: [NFC] Incorrect mapping of Ultralight C in memory

**Original Issue:** [https://github.com/flipperdevices/flipperzero-firmware/issues/4209](https://github.com/flipperdevices/flipperzero-firmware/issues/4209)
**Author:** @mishamyte
**Created:** 2025-05-02T21:39:21Z
**Labels:** NFC, Bug

## Description

### Describe the bug.

According to [Ultralight C datasheet](https://www.nxp.com/docs/en/data-sheet/MF0ICU2.pdf), 16-bytes 3DES key is stored in 4 memory pages. 
It's logically separated to Key1, Key2 with lengths of 8 bytes.

Key1 and Key2 stored in corresponding memory pages in **reverse** order.

![Image](https://github.com/user-attachments/assets/c2902877-e4c3-476a-9803-bff6501d4092)

In current implementation (NFC file version **v4**) data is stored as is, which is conceptually wrong and could lead to unexpected side-effects for tools, which can work with that file. 

For example, key from referenced datasheet sample is stored in a next form:

![Image](https://github.com/user-attachments/assets/1be52048-5ab7-463f-838d-9f45970a7653)

For workflow it's now an issue, because key is also loaded in a memory as is and interpreted correctly.

Behavior can be changed (for persisting/unpersisting key), but it will be a breaking change and potentially can be solved by bumping the schema version (to v5 for example).

### Reproduction

1. Read Mifare Ultralight C with key
2. Save it
3. Open in text editor and check key representation in dump

### Target

_No response_

### Logs

```Text

```

### Anything else?

_No response_

---
*This issue was automatically imported from the upstream Flipper Zero firmware repository.*
