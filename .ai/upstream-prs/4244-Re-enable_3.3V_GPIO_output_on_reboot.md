# PR #4244: Re-enable 3.3V GPIO output on reboot

## Metadata
- **Author:** @aaronjamt (Aaron Tulino)
- **Created:** 2025-07-01
- **Status:** Open
- **Source Branch:** `dev`
- **Target Branch:** `dev`
- **URL:** https://github.com/flipperdevices/flipperzero-firmware/pull/4244

## Labels
None

## Description
# What's new

- While booting, the Flipper Zero firmware resets the BQ25896 registers, disabling 3.3V output to any connected GPIO board. This PR enables the OTG register after the reset if it was enabled before, preventing the connected board from losing power and rebooting.

# Verification 

- Reboot the Flipper Zero (hold Left and Back buttons) while a GPIO board (such as the WiFi Devboard) is connected. Without this commit, the Devboard will light the LED blue as it starts back up after losing power. With this commit, the Devboard does not react to the reboot.

# Checklist (For Reviewer)

- [ ] PR has description of feature/bug or link to Confluence/Jira task
- [ ] Description contains actions to verify feature/bugfix
- [ ] I've built this code, uploaded it to the device and verified feature/bugfix


---
*This PR tracking file was automatically generated from upstream flipperdevices/flipperzero-firmware*
