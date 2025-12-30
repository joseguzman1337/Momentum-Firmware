# PR #4290: Storage: Dont send mount event if SD mounted at boot

## Metadata
- **Author:** @WillyJL (WillyJL)
- **Created:** 2025-10-06
- **Status:** Open
- **Source Branch:** `fix/storage-double-mount-on-boot`
- **Target Branch:** `dev`
- **URL:** https://github.com/flipperdevices/flipperzero-firmware/pull/4290

## Labels
None

## Description
When the switch to `/int` on `/ext` happened, a system was added to load config files when SD card is inserted. I use a similar approach for a few extra things in my fork downstream, and noticed some issues today updating from dev branch. This is not a a new bug here, but rather a side effect of a "bug"/misbehavior that has existed here for a long time.

Most services using this system to load on boot and also on SD card mount do this when starting:
- setup pubsub from storage events
- if SD card is present, load config right away
- when storage pubsub reports SD card mount, load configs

If SD card is present at boot, these services will load config right away, but when storage service finishes starting it will send a SD card mount event, meaning the configs are loaded twice.

In most cases this makes little difference, but for example it means BT keys are loaded twice and BT stack is started twice for no reason. And in my case, I had ble extra beacon setting up at boot with this same system, and just today it started bootlooping because it starts twice and there is probably some race condition somewhere between restarting ble stack and 2 threads wanting to setup ble extra beacon, which made me investigate and notice the double loading.

Some traces of this can be found 3+ years back:
https://github.com/flipperdevices/flipperzero-firmware/blob/85b6b2b8966552a3cd49bf29eae7b0da771dcfa8/applications/system/updater/scenes/updater_scene_main.c#L35-L45
This had a different symptom but seems like same underlying issue of sending SD card mount after storage started. Also wording is a little wrong here, SD card is usually mounted even before storage finishes starting, in `storage_app_alloc()` inside `storage_ext_init()` with `storage_ext_tick_internal()` Sd card is mounted immediately if present, the bug was not about mounting late but about storage tick detecting late that it was mounted.

# What's new

- Fixes this misbehavior by making storage not notify of SD card mount if SD card is present at boot. This way each service can check for itself if SD card is present like they do now, and storage will not send an event shortly after causing a double load
- This approach also fixes the SD card icon in status bar appearing late on boot
- Marking `sd_gui` as already enabled if SD is present means `storage_tick()` will not detect the mount after starting as if it just happened, it already knows it was mounted from init
- I checked all usages of storage pubsub and AFAICT they all check for SD status on boot and load immediately if mounted, meaning all configs should load fine and functionality remain the same, just without double loading now

The alternative would work poorly: if all services did not check for SD card at boot on their own and rely on storage to send the mount event at boot, it could be that one service starts after storage and so it misses the mount event, which would be a tiny subtlety that causes config not to load on boot at all and be unreliable overall.

# Verification 

- No issues booting and loading configs and animations
- Rebooting shows SD card icon in status bar right away
- Updating works fine
- Check logs that eg Bt keys are not loaded twice

# Checklist (For Reviewer)

- [ ] PR has description of feature/bug or link to Confluence/Jira task
- [ ] Description contains actions to verify feature/bugfix
- [ ] I've built this code, uploaded it to the device and verified feature/bugfix


---
*This PR tracking file was automatically generated from upstream flipperdevices/flipperzero-firmware*
