# Issue #4072: Bad USB feature ignores keyboard layout setting (DE-CH)

**Original Issue:** [https://github.com/flipperdevices/flipperzero-firmware/issues/4072](https://github.com/flipperdevices/flipperzero-firmware/issues/4072)
**Author:** @ThWunderlin
**Created:** 2025-01-18T21:04:30Z
**Labels:** USB, Bug

## Description

### Describe the bug.

When using the Bad USB feature with DE-CH keyboard layout selected, the Flipper Zero appears to still send US keyboard scancodes instead of using the selected layout.

### Reproduction

1. Set Flipper Zero Bad USB keyboard layout to DE-CH
2. Connect to MacBook Pro with Swiss German keyboard layout (DE-CH)
3. Run the default Bad USB demo script or a simple test script
4. Observe character mapping issues


Expected behavior:
- Flipper Zero should send correct scancodes matching the selected DE-CH layout
- Special characters should be correctly mapped for Swiss German layout

Actual behavior:
- Flipper Zero sends US keyboard scancodes regardless of selected layout
- This causes incorrect character mapping on Swiss German MacOS:
  - ! becomes +
  - " becomes à
  - § becomes ç
  - ( becomes -
  - ) remains )
  - = becomes ^
  - ? becomes _
  - \ becomes 
  - @ becomes ä
  - # becomes *

Test Environment:
- Device: MacBook Pro
- OS: MacOS with Swiss German (DE-CH) keyboard layout
- Flipper Zero Firmware: [Your firmware version]
- Also tested with Unleashed firmware with same results

Additional Notes:
- Same behavior observed with both official and Unleashed firmware
- Changing Flipper Zero keyboard layout setting has no effect on the output

### Target

_No response_

### Logs

```Text

```

### Anything else?

_No response_

---
*This issue was automatically imported from the upstream Flipper Zero firmware repository.*
