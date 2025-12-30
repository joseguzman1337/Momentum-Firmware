# Security Policy

## Reporting a Vulnerability

If you discover a security vulnerability in Momentum Firmware, please report it responsibly:

1. **Do not** open a public GitHub issue
2. Report via GitHub Security Advisories or contact the maintainers privately
3. Include detailed reproduction steps and impact assessment
4. Allow reasonable time for a fix before public disclosure

## Known Hardware Protocol Limitations

### MIFARE Ultralight C - 3DES Cryptography

**Location**: `lib/nfc/protocols/mf_ultralight/`

The MIFARE Ultralight C implementation uses 3DES (Triple-DES) encryption, which is flagged by security scanners as cryptographically weak. This is **NOT a vulnerability** but a hardware protocol requirement.

**Why 3DES is Used**:
- MIFARE Ultralight C tags (NXP MF0ICU2) mandate 3DES in hardware
- Required for compatibility with millions of deployed NFC tags worldwide
- Cannot be replaced without breaking interoperability with physical devices
- Specified in NXP official datasheets and ISO/IEC 14443-3 Type A

**What This Means**:
- The weakness is in the NFC tag hardware itself, not this implementation
- This code correctly implements the required protocol
- For new deployments, consider NTAG 424 DNA (AES-128) instead
- See `lib/nfc/protocols/mf_ultralight/SECURITY.md` for detailed analysis

**Security Scanner Suppressions**: CodeQL and similar tools will flag 3DES usage. These are false positives for hardware compatibility code.

## Supported Versions

| Version       | Supported          |
| ------------- | ------------------ |
| Latest main   | :white_check_mark: |
| Development   | :white_check_mark: |
| Older commits | :x:                |
