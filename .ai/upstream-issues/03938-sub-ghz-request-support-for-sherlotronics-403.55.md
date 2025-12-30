# Issue #3938: [Sub-Ghz] Request support for Sherlotronics 403.55Mhz Transmitter

**Original Issue:** [https://github.com/flipperdevices/flipperzero-firmware/issues/3938](https://github.com/flipperdevices/flipperzero-firmware/issues/3938)
**Author:** @Axolotl5903
**Created:** 2024-10-11T17:22:47Z
**Labels:** Feature Request, Sub-GHz

## Description

### Sherlotronics TX-6 (6 Button) 403MHz key fob

1. Frequency: 403.55 MHz
2. Modulation: ASK / OOK (Unsure is AM270 / AM650)
3. Dynamic Code (KeeLoq Code-Hopping)
4. RAW Signal Dumps for 3 remotes 

The Flipper Zero is able to detect that the transmitter uses KeeLoq 64 Bit Protocol, as well as the transmitted keys, Hopper code, Button number, and the transmitter's fixed code.
[Sherlotronics Sample1 RAW.sub.txt](https://github.com/user-attachments/files/17345754/Sherlotronics.Sample1.RAW.sub.txt)
[Sherlotronics Sample2 RAW.sub.txt](https://github.com/user-attachments/files/17345755/Sherlotronics.Sample2.RAW.sub.txt)
[Sherlotronics Sample3 RAW.sub.txt](https://github.com/user-attachments/files/17345757/Sherlotronics.Sample3.RAW.sub.txt)

### Anything else?

Hi,
I have a bunch of Sherlotronics TX-6 (6 Button) 403MHz key fobs that I use with Sherlotronics RX1-150 receivers, that I connected to my Garage openers, and would really appreciate it if support for their protocol could be added.

I've verified that the transmitter (remotes) utilizes the HCS301 Chip
I also have a older model of the TX-6 Transmitter (Blue PCB) that I found is also compatible with newer Sherlotronics receivers. I descovered that Sherlotronics did a refresh on all their 2015 transmitters and receivers in 2017, changing from Blue to Green PCB's, and the HSC301 Chip SN Number changed from SN1541 ET4 to SN2117 ET7. 

I also noticed that both PCB's have these 4 contact points on the right side of the PCB, that has the word "PROGRAM" printed next to it, I'm unsure what it's for, but my guess is that there might be a way to program the transmitter.

Sherlotronics is a Local South African Manufacturer, thus their transmitters aren't required to have FCC ID's. However, it does have the following certifications: 
- EN300-220 Nov 1997
- SABS ETSI EN301-489-1:2001
- SABS IEC 60950:1999
- ICASA: TA-2006/759

Any attempt of adding support for this transmitter's protocol would be greatly appreciated, please feel free to contact me if any additional information is required, here is a link to Sherlotronic's official website: https://www.sherlotronics.co.za
I will also attach PDF documents containing additional information of the transmitters and receivers:
https://www.sherlotronics.co.za/wp-content/uploads/2020/09/Sherlo-Keyring-Remote-Control-Sales-Leaflet.pdf
https://www.sherlotronics.co.za/wp-content/uploads/2018/04/TX1_2_4_6_Installation.pdf
https://www.sherlotronics.co.za/wp-content/uploads/2018/04/TX1_2_4_6_ICASA-Certificate.pdf
https://www.sherlotronics.co.za/wp-content/uploads/2018/04/TX1_2_4_6_Product-Declaration.pdf

Thank you!

P.S. I attached the raw subghz files with the extension ".txt" as Github doesn't support .sub files.

---
*This issue was automatically imported from the upstream Flipper Zero firmware repository.*
