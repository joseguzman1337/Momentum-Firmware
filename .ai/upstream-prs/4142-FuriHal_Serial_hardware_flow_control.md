# PR #4142: FuriHal: Serial hardware flow control?

## Metadata
- **Author:** @WillyJL (WillyJL)
- **Created:** 2025-03-09
- **Status:** Open
- **Source Branch:** `feat/serial-flow-ctrl`
- **Target Branch:** `dev`
- **URL:** https://github.com/flipperdevices/flipperzero-firmware/pull/4142

## Labels
None

## Description
# What's new

- @bettse brought up [on the discord server](https://discord.com/channels/740930220399525928/954430078882816021/1348051967141875802) the topic of UART hardware flow control, in specific how the GPIO app USB-UART allows choosing RTS/DTR pins but the code doesn't seem to affect the UART pins behavior
- personally I have no experience with this topic and don't understand it much, but as bettse pointed out the GPIO side in FuriHal is initialized with `HardwareFlowControl = LL_USART_HWCONTROL_NONE` so I thought exposing this as an option to API would be a good start
- neither of use have anything to test this on and I don't have a use for it either, just putting it here in case it makes sense and someone else could find it useful and make it work
- also to note, the USB-UART app mentions RTS/DTR while the stm32 hal has RTS/CTS options, [the difference](https://stackoverflow.com/a/957416/1112230) isn't really clear to either of us

# Verification 

- [ Describe how to verify changes ]

# Checklist (For Reviewer)

- [ ] PR has description of feature/bug or link to Confluence/Jira task
- [ ] Description contains actions to verify feature/bugfix
- [ ] I've built this code, uploaded it to the device and verified feature/bugfix


---
*This PR tracking file was automatically generated from upstream flipperdevices/flipperzero-firmware*
