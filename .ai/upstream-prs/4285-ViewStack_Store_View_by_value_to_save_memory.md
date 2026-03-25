# PR #4285: ViewStack: Store View by value to save memory

## Metadata
- **Author:** @CookiePLMonster (Silent)
- **Created:** 2025-10-03
- **Status:** Open
- **Source Branch:** `view-stack-alloc`
- **Target Branch:** `dev`
- **URL:** https://github.com/flipperdevices/flipperzero-firmware/pull/4285

## Labels
None

## Description
# What's new

This PR changes `ViewStack` to store `View` by value, rather than by a pointer. The stack already has knowledge of View's internals, so this doesn't introduce any new dependencies, but reduces memory usage and fragmentation, as before this change, the view stack was only a pointer to a single view anyway.

Results in a miniscule reduction in memory usage on the main Desktop screen. This is expected, as this change amounts to one allocation less per each ViewStack.

Before:
```
>: free
Free heap size: 142832
Total heap size: 190144
Minimum heap size: 142760
Maximum heap block: 142248
Pool free: 4200
Maximum pool block: 3584

>: free
Free heap size: 142840
Total heap size: 190144
Minimum heap size: 142760
Maximum heap block: 142248
Pool free: 4200
Maximum pool block: 3584
```

After:
```
>: free
Free heap size: 142904
Total heap size: 190144
Minimum heap size: 142376
Maximum heap block: 142328
Pool free: 4200
Maximum pool block: 3584

>: free
Free heap size: 142912
Total heap size: 190144
Minimum heap size: 142376
Maximum heap block: 142328
Pool free: 4200
Maximum pool block: 3584
```

# Verification 

- Verify that the apps using the View Stack (like Desktop) still function correctly.

# Checklist (For Reviewer)

- [ ] PR has description of feature/bug or link to Confluence/Jira task
- [ ] Description contains actions to verify feature/bugfix
- [ ] I've built this code, uploaded it to the device and verified feature/bugfix


---
*This PR tracking file was automatically generated from upstream flipperdevices/flipperzero-firmware*
