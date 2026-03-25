# Issue #4002: RFE: Cannot write NFC-V tag

**Original Issue:** [https://github.com/flipperdevices/flipperzero-firmware/issues/4002](https://github.com/flipperdevices/flipperzero-firmware/issues/4002)
**Author:** @marcmerlin
**Created:** 2024-11-13T21:49:27Z
**Labels:** Feature Request, NFC

## Description

### Describe the enhancement you're suggesting.

### Describe the bug.

I'm using the latest available firmware as of today. I have an NFC-V tag on a water filter that I'd like to duplicate to a blank tag, but copying is not offered for this type of tag, only emulation and that emulation didn't seem to work (my water filter didn't see the emulated tag at all, or didn't like it).

Old versions of flipper zero recognized the tag as ISO15693-3 (unknown)
![image](https://github.com/user-attachments/assets/02741137-2f9d-42f5-803d-099958148f6f)

New (today's) firmware, recognizes the tag as SLIX
![image](https://github.com/user-attachments/assets/e6f7d000-561b-4be0-b5b5-f76c540349fc)

For comparison, the same tag seen by android
![image](https://github.com/user-attachments/assets/eac680fe-b5ba-48d3-b71f-4b94e9551ede)

### Reproduction

Reading the tag works, emulating it seems to work, but at least in my case does not. I can't tell if the emulation is bad or if I have another issue.
But more importantly, there is no 'copy' option that I can find.

I bought these 2 kinds of tags, but currently cannot write to them:
https://www.amazon.com/dp/B0755WF6CK

Any idea what I'm doing wrong, or not supported yet?

### Target

_No response_

### Logs

_No response_

### Anything else?

_No response_

### Anything else?

I may have filed this in the wrong repo originally, namely https://github.com/DarkFlippers/unleashed-firmware/issues/836
apologies for that.
I'm happy to close the other one if appropriate

---
*This issue was automatically imported from the upstream Flipper Zero firmware repository.*
