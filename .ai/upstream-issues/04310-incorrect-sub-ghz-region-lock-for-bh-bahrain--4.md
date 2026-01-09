# Issue #4310: Incorrect Sub-GHz region lock for BH (Bahrain) — 433 MHz should be permitted

**Original Issue:** [https://github.com/flipperdevices/flipperzero-firmware/issues/4310](https://github.com/flipperdevices/flipperzero-firmware/issues/4310)
**Author:** @el7ommed
**Created:** 2025-11-20T07:12:34Z
**Labels:** None

## Description

When the Flipper Zero is provisioned in Bahrain (country code BH), Sub-GHz transmissions on 433.92 MHz AM/OOK are blocked, even though this band is legal for low-power SRD devices in Bahrain.

How to reproduce:
• Device is provisioned as BH through the iOS app
• Record a 433.92 MHz AM remote signal
• Attempt to transmit → Flipper shows: Transmission is Blocked!

Local laws allow the use of these frequencies as per the pdf file below:
PDF : https://www.bahrain.bh/wps/wcm/connect/55803dc3-cae2-4859-9f6d-ce3898df840e/National+Frequency+Plan+2020.pdf?MOD=AJPERES&CVID=njzfrwX
Relevant section: Table at page 47 → “AMATEUR BHR2 - up to 25W”.


What should happen:
The BH region should allow transmissions within 433.05–434.79 MHz, same as EU-style SRD allocations.

---
*This issue was automatically imported from the upstream Flipper Zero firmware repository.*
