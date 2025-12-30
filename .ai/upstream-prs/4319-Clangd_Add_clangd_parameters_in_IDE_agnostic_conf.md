# PR #4319: Clangd: Add clangd parameters in IDE agnostic config file

## Metadata
- **Author:** @WillyJL (WillyJL)
- **Created:** 2025-12-20
- **Status:** Open
- **Source Branch:** `fix/clangd-other-ide`
- **Target Branch:** `dev`
- **URL:** https://github.com/flipperdevices/flipperzero-firmware/pull/4319

## Labels
None

## Description
# What's new

- Clangd now works in other IDE's without IDE specific configuration, eg Zed editor

# Verification 

- Compile firmare, open other editor with clangd support (eg Zed), open a C file, clangd goes through indexing and diagnostics work as expected

# Checklist (For Reviewer)

- [ ] PR has description of feature/bug or link to Confluence/Jira task
- [ ] Description contains actions to verify feature/bugfix
- [ ] I've built this code, uploaded it to the device and verified feature/bugfix


---
*This PR tracking file was automatically generated from upstream flipperdevices/flipperzero-firmware*
