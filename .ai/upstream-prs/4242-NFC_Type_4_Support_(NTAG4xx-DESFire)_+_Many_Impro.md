# PR #4242: NFC: Type 4 Support (NTAG4xx/DESFire) + Many Improvements

## Metadata
- **Author:** @WillyJL (WillyJL)
- **Created:** 2025-06-29
- **Status:** Open
- **Source Branch:** `feat/nfc-type-4-final`
- **Target Branch:** `dev`
- **URL:** https://github.com/flipperdevices/flipperzero-firmware/pull/4242

## Labels
None

## Description
# What's new

I developed this as my final year project for university, as I have now got my results I'm here to upstream it (I was advised not to deal with uni bureaucracy weirdness so I waited until the course was over)

- New Type 4 Tag (NDEF on NTAG4xx / MIFARE DESFire) protocol, full support
- New NTAG4xx (NTAG413 DNA / NTAG424 DNA) protocol, only detection and basic info support
- NDEF parsing plugin supports Type 4 Tag protocol
- Show more version info for MIFARE Plus cards
- Improve detection/verification of MIFARE DESFire and MIFARE Plus SE
- Improve navigation for MIFARE Classic Update from / Write to Initial Card
- Refactor Write code for MIFARE Ultralight/Classic in NFC app helpers
- Cleanup event handling in NFC app
- Refactor NXP Native Commands to share between protocols (used by MIFARE DESFire, MIFARE Plus, NTAG4xx)
- MIFARE DESFire poller API can now switch between native and ISO7816-wrapped commands
- Expand ISO14443-4A API with listener (emulation) support for sending responses to reader (except I-block chaining)
- Exposed some APIs for apps to use that were meant to be public:
  - ISO14443-3A listener (emulation)
  - ISO15693-3 device (data), poller (reading), listener (emulation)
- Cleanup/reorder protocol definitions for tidiness

![image](https://github.com/user-attachments/assets/af69b897-dc95-48f7-bb96-f17afee43226)
![image](https://github.com/user-attachments/assets/d2eda789-a787-42b9-8783-64d638260abf)
![image](https://github.com/user-attachments/assets/fe5bc4d0-dfc5-4e24-a7cd-70d4d86cfebd)
![image](https://github.com/user-attachments/assets/0bcca699-4d61-44f2-9a85-e04e77ffb0ff)

# Verification 

- Test that reading, parsing, writing and emulating of NTAG4xx and MIFARE DESFire containing NDEF data works as expected
- Test that writing MIFARE Ultralight / Classic works as before
- Test that reading MIFARE Plus EV1/2 shows extra version info in More > Info > More (just like NTAG4xx and similar to DESFire "Card Info" option)
- If possible test reading original MF3ICD40 DESFire to ensure other changes did not break compatibility with pre-ISO7816 DESFire
- Test that Edit UID options in NFC app (where applicable) work as before

# Checklist (For Reviewer)

- [ ] PR has description of feature/bug or link to Confluence/Jira task
- [ ] Description contains actions to verify feature/bugfix
- [ ] I've built this code, uploaded it to the device and verified feature/bugfix


---
*This PR tracking file was automatically generated from upstream flipperdevices/flipperzero-firmware*
