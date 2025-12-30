# PR #4286: Make more data const to move it to `.rodata`

## Metadata
- **Author:** @CookiePLMonster (Silent)
- **Created:** 2025-10-04
- **Status:** Open
- **Source Branch:** `more-const-data`
- **Target Branch:** `dev`
- **URL:** https://github.com/flipperdevices/flipperzero-firmware/pull/4286

## Labels
None

## Description
# What's new

I disassembled the firmware to find out more instances of writable data that can be moved to `.rodata`, and thus save RAM on runtime.

Before:
```
.text         600348 (586.28 K)
.rodata       165956 (162.07 K)
.data            680 (  0.66 K)
.bss            4748 (  4.64 K)
.free_flash   281252 (274.66 K)
```

After:

```
.text         600316 (586.25 K)
.rodata       166220 (162.32 K)
.data            420 (  0.41 K)
.bss            4748 (  4.64 K)
.free_flash   281280 (274.69 K)
```

Saves 260 bytes of `.data`, so it should result in similar reduction of RAM usage across the board.

# Verification 

General regression test is needed.

# Checklist (For Reviewer)

- [ ] PR has description of feature/bug or link to Confluence/Jira task
- [ ] Description contains actions to verify feature/bugfix
- [ ] I've built this code, uploaded it to the device and verified feature/bugfix


---
*This PR tracking file was automatically generated from upstream flipperdevices/flipperzero-firmware*
