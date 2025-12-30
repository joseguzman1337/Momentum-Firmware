# PR #3561: iButton Dallas DS1904 (RTC) support

## Metadata
- **Author:** @bettse (Eric Betts)
- **Created:** 2024-04-02
- **Status:** Open
- **Source Branch:** `ibutton_ds1904`
- **Target Branch:** `dev`
- **URL:** https://github.com/flipperdevices/flipperzero-firmware/pull/3561

## Labels
`New Feature`, `iButton`

## Description
# What's new

- iButton Dallas DS1904 (RTC) support
- Rough draft, I was targeting reading/writing of the iButtons since I don't have a way to test emulation.

# Verification 

- Scan DS1904 and see it detected and time shown
- TBD: How to handle "write" to set the clock and "device control byte"

# Checklist (For Reviewer)

- [ ] PR has description of feature/bug or link to Confluence/Jira task
- [ ] Description contains actions to verify feature/bugfix
- [ ] I've built this code, uploaded it to the device and verified feature/bugfix


---
*This PR tracking file was automatically generated from upstream flipperdevices/flipperzero-firmware*
