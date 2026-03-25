# PR #4297: Make FDX-B readout more descriptive

## Metadata
- **Author:** @snowsign (Skye Gibbs)
- **Created:** 2025-10-21
- **Status:** Open
- **Source Branch:** `fdxb-info`
- **Target Branch:** `dev`
- **URL:** https://github.com/flipperdevices/flipperzero-firmware/pull/4297

## Labels
None

## Description
# What's new

The ISO 11784 standard for FDX-B includes a couple fields that weren't included in the firmware. This PR just adds those remaining fields, including the "Starting digit of the visual number" field introduced in the 2024 edition of the standard.

## Fields added
- Visual start digit
- Replacement/retagging number
- User info
- Data block status
- RUDI bit
- Reserved for future use

The shortened names and order of the fields are just what make sense to me, so feel free to provide suggestions.

# Verification 

1. Create an FDX-B formatted LFRFID file manually or by using something like a proxmark3
2. View the file in the RFID app
3. Under "Info", check that the fields are formatted correctly and match up with you set them to

# Checklist (For Reviewer)

- [ ] PR has description of feature/bug or link to Confluence/Jira task
- [ ] Description contains actions to verify feature/bugfix
- [ ] I've built this code, uploaded it to the device and verified feature/bugfix


---
*This PR tracking file was automatically generated from upstream flipperdevices/flipperzero-firmware*
