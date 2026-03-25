# PR #3861: [FL-3348] Software SPI

## Metadata
- **Author:** @portasynthinca3 (Anna Antonenko)
- **Created:** 2024-08-29
- **Status:** Open
- **Source Branch:** `portasynthinca3/3348-softspi`
- **Target Branch:** `dev`
- **URL:** https://github.com/flipperdevices/flipperzero-firmware/pull/3861

## Labels
None

## Description
# What's new
  - Software SPI library (master mode only)
  - SPI testing app (`spi_test`)

# Verification
  - Connect a logic analyzer or an oscilloscope to pins PA7 (MOSI), PB3 (SCK) and PA4 (CS)
  - Bridge pins PA6 (MISO) and PA7 (MOSI) together
  - Launch the `spi_test` app
  - Select "Software TRX"
  - Verify that the signal looks good
  - Verify that the logs say `sent 55 AA, received 55 AA`
  
# Waveforms
Hardware SPI:
![hardspi](https://github.com/user-attachments/assets/9c9659a6-19b5-4249-846c-672f978f45c8)

Software SPI (far away, CS transitions visible):
![softspi_far](https://github.com/user-attachments/assets/ff26d334-aa96-4b21-97e1-7cdaf37a4949)

Software SPI (up close, no CS transitions visible):
![softspi_close](https://github.com/user-attachments/assets/babc7167-a33f-4e04-a0b3-444c70b0466e)

# Checklist (For Reviewer)

- [ ] PR has description of feature/bug or link to Confluence/Jira task
- [ ] Description contains actions to verify feature/bugfix
- [ ] I've built this code, uploaded it to the device and verified feature/bugfix


---
*This PR tracking file was automatically generated from upstream flipperdevices/flipperzero-firmware*
