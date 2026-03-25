# PR #4171: Retries on QA jobs

## Metadata
- **Author:** @doomwastaken (Konstantin Volkov)
- **Created:** 2025-04-02
- **Status:** Open
- **Source Branch:** `doom/retries-on-qa-jobs`
- **Target Branch:** `dev`
- **URL:** https://github.com/flipperdevices/flipperzero-firmware/pull/4171

## Labels
None

## Description
# What's new

3 attempts to complete any job. Should only do if job timed out (i.e. lost flipper), should not start new ones if job failed or passed!

# Verification 

Check no retries if we "skip" "fail" "succeed".
Check for 2 retries for timeouts

# Checklist (For Reviewer)

- [ ] PR has description of feature/bug or link to Confluence/Jira task
- [ ] Description contains actions to verify feature/bugfix
- [ ] I've built this code, uploaded it to the device and verified feature/bugfix


---
*This PR tracking file was automatically generated from upstream flipperdevices/flipperzero-firmware*
