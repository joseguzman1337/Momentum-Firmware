# Issue #3867: Flipper misidentifies Visonic_Powecode alarm signal as Dickert_MAHS.

**Original Issue:** [https://github.com/flipperdevices/flipperzero-firmware/issues/3867](https://github.com/flipperdevices/flipperzero-firmware/issues/3867)
**Author:** @Hamika20
**Created:** 2024-09-02T20:01:00Z
**Labels:** Sub-GHz, Bug

## Description

### Describe the bug.

I think I've found a bug with this new protocol called Dickert_MAHS. I receive this signal multiple times a day, even though I live in a rural area far away from other garages. I receive the signal about 30 times a day. Even at midnight. When I use RTL433, the signal appears as a Visonic-Powercode sensor. I'm not sure if the Flipper is misidentifying the sensor's signal or if something else is happening.


![Screenshot-20240902-223327dd](https://github.com/user-attachments/assets/8242ceba-bacf-40c4-afee-04430dabd900)
![Screenshot-20240902-222130flip](https://github.com/user-attachments/assets/4492a432-f5c2-41fb-94c2-ae673733ec10)
![Screenshot_2024-08-28_174412](https://github.com/user-attachments/assets/8de0ba56-6f9d-49fe-baef-4300b609857d)


### Reproduction

I copied the signal from the remote and tried replaying it, but RTL433 didn't recognize it at all.
I think I will need to further investigate and try to find a similar motion detector and trigger it manually.

### Target

Devs

### Logs

_No response_

### Anything else?

_No response_

---
*This issue was automatically imported from the upstream Flipper Zero firmware repository.*
