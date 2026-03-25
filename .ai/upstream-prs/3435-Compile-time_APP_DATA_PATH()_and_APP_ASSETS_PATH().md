# PR #3435: Compile-time APP_DATA_PATH() and APP_ASSETS_PATH()

## Metadata
- **Author:** @WillyJL (WillyJL)
- **Created:** 2024-02-09
- **Status:** Open
- **Source Branch:** `compile-time-app-paths`
- **Target Branch:** `dev`
- **URL:** https://github.com/flipperdevices/flipperzero-firmware/pull/3435

## Labels
`Build System & Scripts`, `Core+Services`

## Description
# What's new

- `APP_DATA_PATH()` and `APP_ASSETS_PATH()` use `appid` from compile time instead of runtime `thread_id`
- Fixes incorrect paths when these app storage macros are used in timer / service context (eg. timer/draw callback)
- Less runtime overhead due to less string replacing to generate correct paths
- Code not compiled as FAP will fail since FAP_APPID is not defined
- No user intervention required, this is drop in fix, only recompile is needed
- To function, adds C define `FAP_APPID`, could be useful to app makers aswell

# Verification 

- Open app that uses `APP_DATA_PATH()` or `APP_ASSETS_PATH()` in draw/timer callback
- Path is still correct `/ext/apps_.../appid`, instead of ending as `/ext/apps_.../system` or `/ext/apps_.../gui`

# Checklist (For Reviewer)

- [ ] PR has description of feature/bug or link to Confluence/Jira task
- [ ] Description contains actions to verify feature/bugfix
- [ ] I've built this code, uploaded it to the device and verified feature/bugfix


---
*This PR tracking file was automatically generated from upstream flipperdevices/flipperzero-firmware*
