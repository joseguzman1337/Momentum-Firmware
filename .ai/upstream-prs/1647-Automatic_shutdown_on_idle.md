# PR #1647: Automatic shutdown on idle

## Metadata
- **Author:** @SHxKenzuto ()
- **Created:** 2022-08-23
- **Status:** Open
- **Source Branch:** `shutdown_idle`
- **Target Branch:** `dev`
- **URL:** https://github.com/flipperdevices/flipperzero-firmware/pull/1647

## Labels
`UI`, `New Feature`, `Core+Services`

## Description
# What's new

- Added an option under [Settings->Power] that allows Flipper to be automatically turned off after a certain amount of time has passed without input from user ( the options are 15min, 30min, 1h, 2h, 6h, 12h, 24h, 48h).

# Verification 

- A submenu named [Shutdown on Idle] has been added under [Settings->Power]. Under that submenu is possible to set how long Flipper will be idle before shutting off on his own and to turn off this feature.

# Checklist (For Reviewer)

- [ ] PR has description of feature/bug or link to Confluence/Jira task
- [ ] Description contains actions to verify feature/bugfix
- [ ] I've built this code, uploaded it to the device and verified feature/bugfix


---
*This PR tracking file was automatically generated from upstream flipperdevices/flipperzero-firmware*
