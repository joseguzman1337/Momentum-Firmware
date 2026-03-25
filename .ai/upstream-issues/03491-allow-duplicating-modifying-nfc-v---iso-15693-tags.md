# Issue #3491: Allow duplicating/modifying NFC-V / ISO 15693 tags to get write new lifeionizers NFC tags

**Original Issue:** [https://github.com/flipperdevices/flipperzero-firmware/issues/3491](https://github.com/flipperdevices/flipperzero-firmware/issues/3491)
**Author:** @marcmerlin
**Created:** 2024-03-01T16:07:37Z
**Labels:** Feature Request, NFC

## Description

### Describe the enhancement you're suggesting.

I have a water filter that reads NFC-V tags to see if I put a new filter in (and force me to keep buying more even if replacement is not actually needed yet).  It's a LIFE IONIZER MXL-9 ALKALINE WATER IONIZER from lifeionizers.com (to help google searches get here).
Flipper zero can read the NFC-V tag and emulate it, but what I actually need it to do is to read the tag and allow me to rewrite it on a blank tag.  I have bought these: 
NXP iCode SLIX Tag,ISO/IEC 15693 HF,RFID Library Labels (Pack of 20)  https://www.amazon.com/gp/product/B0755WF6CK
but flipper zero does not seem to allow to rewrite/duplicate a tag in the case of NFC-V.
I should add that in this specific case, I'm not actually actually trying to duplicate the tag exactly but will want to modify a few bytes (maybe just the serial number, or a few bytes in the payload) to have the water filter think it's a new filter and work again.
More info for anyone curious: the water filter will refuse to work if too many liters have been filtered (which is fair enough), but also will time out a filter after about a year of clock time, even if it's barely been used and that's the bad part. I did find a workaround where putting in another filter resets the clock time on the new filter and then later also allows reusing the first filter (it remembers how many liters for the last few filters, but not how many days of use, so that gets reset).
That workaround is helpful, but having flipper zero allow me to write new tags after editting a few bytes, would be even better.
As for the last question: how could I have the new tag be read: the filter fits in 2 ways, one direction has no tag and the other direction has the embedded tag. I woudl somply glue the new tag on the other side and put the filter that way, the old tag would be too far and the new tag would be read.

### Anything else?

_No response_

---
*This issue was automatically imported from the upstream Flipper Zero firmware repository.*
