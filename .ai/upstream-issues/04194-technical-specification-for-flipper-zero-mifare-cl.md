# Issue #4194: Technical Specification for Flipper Zero Mifare Classic 1K Enhancement

**Original Issue:** [https://github.com/flipperdevices/flipperzero-firmware/issues/4194](https://github.com/flipperdevices/flipperzero-firmware/issues/4194)
**Author:** @x133t
**Created:** 2025-04-19T17:33:16Z
**Labels:** NFC, Triage

## Description

### Describe the enhancement you're suggesting.

## 1. Introduction

I have tested the Flipper Zero with ISO14443-A MIFARE Classic 1K standard and discovered several serious issues that need to be addressed. These problems are particularly acute when working with tags that have an MF filter.

## 2. Issues Discovered

### 2.1 Problems with Iron Logic technology.

There is an issue with dumping data from cards and key vulnerabilities in Mifare Classic 1k cards programmed by an intercom company that uses Iron Logic readers.

KDF is a key derivation function. It's possible to calculate the key by knowing the UID in Mifare Classic 1k cards, definitely using at least 4 bytes. This was accomplished by the Russian company ikeybase, but for some reason no one has been able to crack this algorithm, and they keep it secret—they have access to sector 14 KK KeyA. If you have any hints about how this works, specifically how the prediction key is calculated from the UID, I would be very grateful.

### 2.2 Problems with Unknown Keys

I also tested another tag with UID 96B8A921 (with MF3 filter), whose keys were unknown to me. The key recovery methods built into Flipper Zero proved ineffective - it takes too much time. I tried using various known vulnerabilities (nested, hardnested, darkside), but none of them helped.

However, TMD-5S and SMKey with ikeybase express software very quickly recovered the keys through their server algorithm:

- Key A: EF 41 40 37 DC F6
- Key B: B6 DA 90 FE 2D E0

When I took these keys and used Flipper Zero to write to an empty MF3 tag, the result was successful - the copy opened the intercom door.

### 2.3 Problems with Reading Sectors

I also noticed that Flipper Zero doesn't always reliably read all sectors. This depends on the type of tag - some are read completely, others only partially.

## 3. Required Improvements

### Test 1: Working with system KDF

We need to try implementing a KDF for sector 14 that would generate keys based on the UID.

### Test 2: Recovery of Unknown Keys

Tag with unknown keys (for example, with UID 96B8A921) and I will verify that:

- Keys are recovered within a reasonable time (no more than 2 minutes)
- The recovered keys are correct (for example, Key A: EF 41 40 37 DC F6, Key B: B6 DA 90 FE 2D E0)
- When writing data to an empty MF3 tag, the copy works like the original

### Test 3: Reading Stability

I will check various types of tags with MF3 filter and be convinced that:

- All sectors are successfully read
- Or for example, implement a nested attack in a phone application with Bluetooth connection to the Flipper. The application would take the file from the log in ext/nfc/.nested.log and the smartphone copies it via Bluetooth, converts .nested.log to .nonce format, and then decrypts it from .nonce to .nfc dictionary by itself, as smartphones have more computing power.
- Reading results are stable during repeated scans of the same tag.


[test_original.nfc.json](https://github.com/user-attachments/files/19822212/test_original.nfc.json)

[hf-mf-E3D143BD-dump.json](https://github.com/user-attachments/files/19822215/hf-mf-E3D143BD-dump.json)

[test_E3D143BD.nfc.json](https://github.com/user-attachments/files/19822232/test_E3D143BD.nfc.json)

[96B8A921.nfc.json](https://github.com/user-attachments/files/19822211/96B8A921.nfc.json)
[2573B480.nfc.json](https://github.com/user-attachments/files/19822210/2573B480.nfc.json)

[Video: Original Tag](https://youtu.be/PUBvl1T7aiY)

---
*This issue was automatically imported from the upstream Flipper Zero firmware repository.*
