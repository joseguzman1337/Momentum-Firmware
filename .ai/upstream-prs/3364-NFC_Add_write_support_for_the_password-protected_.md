# PR #3364: NFC: Add write support for the password-protected MF ultralight tag

## Metadata
- **Author:** @nekolab (Yi S.)
- **Created:** 2024-01-14
- **Status:** Open
- **Source Branch:** `feat/mf-ultralight-write-with-password`
- **Target Branch:** `dev`
- **URL:** https://github.com/flipperdevices/flipperzero-firmware/pull/3364

## Labels
`NFC`, `New Feature`

## Description
# What's new
* Add write capability for password-protected MF Ultralight tags.
* Fix the check condition in `mf_ultralight_poller_handler_read_tearing_flags`. Support for `MfUltralightFeatureSupportSingleCounter` doesn't imply support for reading tearing flags, as seen in NTAG21x series.
* Revised MF Ultralight poller logic from `auth => read **THEN** write` to `auth => read **OR** write`. According to NXP specifications, NTAG commands should maintain the tag in `ACTIVE` or `AUTHENTICATED` state. However, some compatible tags deviate from this spec and accept only one read/write command in the `AUTHENTICATED` state. This change addresses write command failures because in the previous logic it would issued after the read commands.
* More debug logs to provide users with better NFC status insights without needing to rebuild the firmware.

# Verification 
Testing was conducted on an NTAG shipped with an air purifier:
* Read, unlock, and save the tag first. Modified a sector and wrote it back to the NFC tag without issues. The altered sector was correctly read in subsequent actions.
* Attempted to write with an incorrect password resulted in expected write failure.

Additional testing on devices without password protection needs reviewer's help due to limited device availability.


# Checklist (For Reviewer)

- [ ] PR has description of feature/bug or link to Confluence/Jira task
- [ ] Description contains actions to verify feature/bugfix
- [ ] I've built this code, uploaded it to the device and verified feature/bugfix


---
*This PR tracking file was automatically generated from upstream flipperdevices/flipperzero-firmware*
