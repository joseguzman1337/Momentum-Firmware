# PR #4313: NFC: Make NFC app startup from fav's faster

## Metadata
- **Author:** @xMasterX (MMX)
- **Created:** 2025-12-01
- **Status:** Open
- **Source Branch:** `nfs_most_wanted`
- **Target Branch:** `dev`
- **URL:** https://github.com/flipperdevices/flipperzero-firmware/pull/4313

## Labels
None

## Description
# What's new

- Extra parsers for various transportation cards and other now show loading animation and will be loaded only when they are required, for example launching emulation scene from favourites doesn't use them, so in result we have much faster loading

# Verification 

- Try opening saved NFC file from archive (desktop - down arrow) without this change and then apply this patch
- See difference
- Try reading supported (transport) card via regular Read mode 

# Checklist (For Reviewer)

- [ ] PR has description of feature/bug or link to Confluence/Jira task
- [ ] Description contains actions to verify feature/bugfix
- [ ] I've built this code, uploaded it to the device and verified feature/bugfix


---
*This PR tracking file was automatically generated from upstream flipperdevices/flipperzero-firmware*
