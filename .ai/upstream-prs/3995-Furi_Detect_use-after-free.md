# PR #3995: Furi: Detect use-after-free

## Metadata
- **Author:** @WillyJL (WillyJL)
- **Created:** 2024-11-09
- **Status:** Open
- **Source Branch:** `use-after-free-sentinel`
- **Target Branch:** `dev`
- **URL:** https://github.com/flipperdevices/flipperzero-firmware/pull/3995

## Labels
None

## Description
# What's new

- `free()` now marks memory with `0xDD`
- `BusFault` handler checks for `0xDDDDDDDD` and 64K after it to determine "Possible use-after-free"
- if such memory address is not dereferenced no crash will happen, but this change is still useful while debugging, as seeing 0xDD in your data is a clear giveaway of use-after-free
- added back `BusFault` handler extra logging from old TLSF experiment
- fixed atomicity in `furi_semaphore_release()`:
  - if thread A is waiting for acquire() and thread B calls release()
  - then halfway through release() code, A would wake up and continue, before B finishes release()
  - this could cause use-after-free if A free()s semaphore after acquire(), because after this B would finish release() which dereferences instance->event_loop_link
  - for example, RpcCli had this use-after-free:
    - `rpc_cli_command_start_session()` is waiting for `furi_semaphore_acquire()`
    - `rpc_cli_session_terminated_callback()` will `furi_semaphore_release()`
    - this wakes up `rpc_cli_command_start_session()` which then does furi_semaphore_free()
    - later, `furi_semaphore_release()` inside of `rpc_cli_session_terminated_callback()` resumes, and dereferences the semaphore that `rpc_cli_command_start_session()` has already free'd
  - there might be more similar issues with event loop items being used after yielding, which would break atomicity and lead to possible use-after-free, but i have not looked for them or found other crashes like this yet

# Verification 

- test anything and everything for hidden use-after-free that were unknown until now

# Checklist (For Reviewer)

- [ ] PR has description of feature/bug or link to Confluence/Jira task
- [ ] Description contains actions to verify feature/bugfix
- [ ] I've built this code, uploaded it to the device and verified feature/bugfix


---
*This PR tracking file was automatically generated from upstream flipperdevices/flipperzero-firmware*
