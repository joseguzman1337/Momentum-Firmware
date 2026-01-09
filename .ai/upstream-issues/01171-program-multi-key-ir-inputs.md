# Issue #1171: Program multi-key IR inputs

**Original Issue:** [https://github.com/flipperdevices/flipperzero-firmware/issues/1171](https://github.com/flipperdevices/flipperzero-firmware/issues/1171)
**Author:** @edbrannin
**Created:** 2022-04-26T20:12:19Z
**Labels:** Feature Request, Infrared, UI

## Description

**Is your feature request related to a problem? Please describe.**

I'd like to save a sequence of IR signals to replay from the Flipper, like:

- TV Input, TV 2
- TV power on, Receiver power on, Receiver input X

**Describe the solution you'd like**

Today: When recording a new IR payload, as soon as the Flipper recognizes a signal, it stops listening and prompts to [RETRY, SEND, SAVE].

Maybe add an ADD option to make the Flipper capture a second signal to play after the first?

**Describe alternatives you've considered**

Other options include:

- Crafting macros from the IR app (more flexibility, but there are UX challenges; we can't even reorder custom remote buttons yet)
- Crafting macros from the Mobile apps (Simpler UX, but requires an additional device for setup)
- Sending IR-app-recorded signals from a compiled Application (those can't be sideloaded yet, and it would limit this sort of thing to programmers)

**Additional context**

[`u/skotozavr`](https://www.reddit.com/user/skotozavr/) [suggested I report this issue from Reddit](https://www.reddit.com/r/flipperzero/comments/tzy80f/can_you_do_multiplea_series_of_infrared_replays/)

---
*This issue was automatically imported from the upstream Flipper Zero firmware repository.*
