# PR #4264: Update microel.c

## Metadata
- **Author:** @grugnoymeme (47LeCoste)
- **Created:** 2025-08-13
- **Status:** Open
- **Source Branch:** `dev`
- **Target Branch:** `dev`
- **URL:** https://github.com/flipperdevices/flipperzero-firmware/pull/4264

## Labels
`NFC`, `New Feature`

## Description
# What's new

This update enhances the Microel card parser by adding support for extracting additional data fields from the Mifare Classic 1K card, including:

Basic card information:

UID
ATQA
SAK

Extended data fields:

Vendor ID
Available credit
Last transaction details
Transaction date
Operation number
Operation type
Admission credit
Deposit status (Yes/No)
Points balance
Previous credit amount
Date of previous credit

These additions improve the accuracy and completeness of the parsed data.

# Checklist (For Reviewer)

- [ ] PR has description of feature/bug or link to Confluence/Jira task
- [ ] Description contains actions to verify feature/bugfix
- [ ] I've built this code, uploaded it to the device and verified feature/bugfix


---
*This PR tracking file was automatically generated from upstream flipperdevices/flipperzero-firmware*
