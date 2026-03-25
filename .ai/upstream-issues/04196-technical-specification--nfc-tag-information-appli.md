# Issue #4196: Technical Specification: NFC Tag Information Application for Flipper Zero

**Original Issue:** [https://github.com/flipperdevices/flipperzero-firmware/issues/4196](https://github.com/flipperdevices/flipperzero-firmware/issues/4196)
**Author:** @x133t
**Created:** 2025-04-19T18:35:44Z
**Labels:** NFC, Triage

## Description

### Description of the feature you're suggesting.

## Project Overview

I need an application for Flipper Zero that will read detailed information about NFC tags, similar to how Proxmark, TMD-5S, or SMKey devices operate. This should be a standalone application that quickly identifies the tag type before proceeding to read it with the scanner.

## Application Requirements

I want the application to:

- Scan ISO14443-A tags (primarily MIFARE Classic 1K standard)
- Display all critical technical information about the tag:
  - UID (unique identifier)
  - ATQA
  - SAK
  - Tag type (e.g., "MIFARE Classic 1K")
  - RATS support status
  - Static nonce information
  - Hints for further actions

It's especially important that the application can detect the presence and type of filter on the tag (MF1, MF2, MF3, OTP, ZERO, and others).

## Current Issues

I've attempted to write this application myself but encountered errors. In my implementation, the application doesn't detect filters like TDM-5S or Proxmark do, and produces the following errors in the logs:

```
122528 [D][Nfc] FWT Timeout
122579 [E][Iso14443_4aPoller] ATS request failed
122582 [D][Iso14443_4aPoller] Failed to read ATS
```

## Development Considerations

- The application should work quickly (no more than 3 seconds per scan)
- It should handle errors correctly
- It should use the NFC libraries from the Flipper Zero SDK
- It should implement retry attempts to improve reliability

I've attached the source code of my implementation for further analysis and development. I would appreciate help in solving these issues!

[TMD-5S](https://github.com/user-attachments/assets/58530c2b-cdd7-4102-91b4-5878d1410d58)

[Video: Check NFC](https://youtu.be/dH3hJeDYR00)

[Nfc Tag Detector.zip](https://github.com/user-attachments/files/19822442/Nfc.Tag.Detector.zip)

---
*This issue was automatically imported from the upstream Flipper Zero firmware repository.*
