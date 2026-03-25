# PR #4298: NFC: Synchronise `mf_classic_dict.nfc` with `mfc_default_keys.dic`

## Metadata
- **Author:** @ry4000 ()
- **Created:** 2025-10-25
- **Status:** Open
- **Source Branch:** `dev`
- **Target Branch:** `dev`
- **URL:** https://github.com/flipperdevices/flipperzero-firmware/pull/4298

## Labels
None

## Description
# What's new

- [**`mf_classic_dict.nfc`**](https://github.com/flipperdevices/flipperzero-firmware/blob/dev/applications/main/nfc/resources/nfc/assets/mf_classic_dict.nfc) was synchronised with [**`mfc_default_keys.dic`**](https://github.com/RfidResearchGroup/proxmark3/blob/master/client/dictionaries/mfc_default_keys.dic) as of [**#3007**](https://github.com/RfidResearchGroup/proxmark3/pull/3007), which means:
  - New keys were added to the dictionary.
  - Some duplicate keys were removed from the dictionary.
  - Two keys had their `# ` prefix removed *making them valid keys once again*.

# Verification 

- Compare [**History for `mfc_default_keys.dic`**](https://github.com/RfidResearchGroup/proxmark3/commits/master/client/dictionaries/mfc_default_keys.dic) against [**#3007**](https://github.com/RfidResearchGroup/proxmark3/pull/3007).
- Check that the following keys appear once only in [**`mfc_default_keys.dic`**](https://github.com/RfidResearchGroup/proxmark3/blob/master/client/dictionaries/mfc_default_keys.dic):
  - `7b296f353c6b` in [**L801**](https://github.com/RfidResearchGroup/proxmark3/blob/bf0330db93a78d79a21c3c7131bec1fe645b4ae6/client/dictionaries/mfc_default_keys.dic#L801);
  - `3fa7217ec575` in [**L815**](https://github.com/RfidResearchGroup/proxmark3/blob/bf0330db93a78d79a21c3c7131bec1fe645b4ae6/client/dictionaries/mfc_default_keys.dic#L815);
  - `a0a1a2a3a4a5` in [**L14**](https://github.com/RfidResearchGroup/proxmark3/blob/bf0330db93a78d79a21c3c7131bec1fe645b4ae6/client/dictionaries/mfc_default_keys.dic#L14); and,
  - `ffffffffffff` in [**L8**](https://github.com/RfidResearchGroup/proxmark3/blob/bf0330db93a78d79a21c3c7131bec1fe645b4ae6/client/dictionaries/mfc_default_keys.dic#L8).
- Check that the following keys no longer have `# ` prefixed in [**`mfc_default_keys.dic`**](https://github.com/RfidResearchGroup/proxmark3/blob/master/client/dictionaries/mfc_default_keys.dic):
  - `049979614077` in [**L343**](https://github.com/RfidResearchGroup/proxmark3/blob/bf0330db93a78d79a21c3c7131bec1fe645b4ae6/client/dictionaries/mfc_default_keys.dic#L343); and,
  - `829338771705` in [**L344**](https://github.com/RfidResearchGroup/proxmark3/blob/bf0330db93a78d79a21c3c7131bec1fe645b4ae6/client/dictionaries/mfc_default_keys.dic#L344).

# Checklist (For Reviewer)

- [ ] PR has description of feature/bug or link to Confluence/Jira task
- [ ] Description contains actions to verify feature/bugfix
- [ ] I've built this code, uploaded it to the device and verified feature/bugfix


---
*This PR tracking file was automatically generated from upstream flipperdevices/flipperzero-firmware*
