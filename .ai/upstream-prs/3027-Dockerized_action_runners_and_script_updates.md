# PR #3027: Dockerized action runners and script updates

## Metadata
- **Author:** @doomwastaken (Konstantin Volkov)
- **Created:** 2023-08-31
- **Status:** Open
- **Source Branch:** `doom/dockerized_action_runners`
- **Target Branch:** `dev`
- **URL:** https://github.com/flipperdevices/flipperzero-firmware/pull/3027

## Labels
None

## Description
# What's new

- All test actions (unit, updater and integration) should be able to run on any dockerized runner 
- Moved all scripts/testing into scripts/testops.py
- Automatic device detection
- New device reset scenario on any failure (flash under reset)

# Verification 

- Unit, Updater and Integration test runs pass
- Runners should be able to stop for maintenance and restart after
- Multiple runs could be going simultaneously, up to number of physical devices connected
- Flipper and STLink should be selected automatically

# Checklist (For Reviewer)

- [ ] PR has description of feature/bug or link to Confluence/Jira task
- [ ] Description contains actions to verify feature/bugfix
- [ ] I've built this code, uploaded it to the device and verified feature/bugfix


---
*This PR tracking file was automatically generated from upstream flipperdevices/flipperzero-firmware*
