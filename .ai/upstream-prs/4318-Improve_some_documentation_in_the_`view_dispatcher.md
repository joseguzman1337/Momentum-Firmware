# PR #4318: Improve some documentation in the `view_dispatcher` and `view_port`

## Metadata
- **Author:** @loftyinclination (lofty)
- **Created:** 2025-12-19
- **Status:** Open
- **Source Branch:** `callback-documentation`
- **Target Branch:** `dev`
- **URL:** https://github.com/flipperdevices/flipperzero-firmware/pull/4318

## Labels
None

## Description
# What's new

- The only changes in this patch are to documentation. A number of call sites and usages have been added, with \see tags to link to other parts of the code that are related.
- This was motivated by an attempt to write safe FFI bindings in Rust, which has constraints on how code might be shared between threads. The new information in this documentation should hopefully make that process smoother.

# Verification 

- The details about the calling thread should be checked.
- The doxygen special commands might need some tweaking/changing.

# Checklist (For Reviewer)

- [ ] PR has description of feature/bug or link to Confluence/Jira task
- [ ] Description contains actions to verify feature/bugfix
- [ ] I've built this code, uploaded it to the device and verified feature/bugfix


---
*This PR tracking file was automatically generated from upstream flipperdevices/flipperzero-firmware*
