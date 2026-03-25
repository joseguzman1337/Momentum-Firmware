# Issue #4106: NFC Reading Issue with ISO 14443-3A Mifare Ultralight Card

**Original Issue:** [https://github.com/flipperdevices/flipperzero-firmware/issues/4106](https://github.com/flipperdevices/flipperzero-firmware/issues/4106)
**Author:** @suaveolent
**Created:** 2025-02-12T08:52:02Z
**Labels:** Feature Request, NFC

## Description

### Describe the bug.

When attempting to read an ISO 14443-3A Mifare Ultralight card (ATQA: 0x0044, SAK: 0x00), the Flipper Zero device gets stuck on the "Don't Move" screen. The debug output indicates multiple FWT timeouts and failures in reading the ATS and signature from the card.

If I read it as "Specific Card Type" and select ISO14443-3A is correctly identifies the UID, however shows it as ISO14443-3A (Unknown)

### Reproduction

1. Attempt to read above mentioned ISO 14443-3A Mifare Ultralight card with the NFC application
2. Observe the device getting stuck on the "Don't Move" screen.

### Target

_No response_

### Logs

```Text
489563 [D][NfcScanner] Found 5 base protocols
489568 [D][DolphinState] icounter 1065, butthurt 14
489603 [D][Nfc] FWT Timeout
489626 [D][Nfc] FWT Timeout
489677 [D][Nfc] FWT Timeout
489699 [D][Nfc] FWT Timeout
489725 [D][NfcScanner] Found 5 children
489769 [D][Nfc] FWT Timeout
489802 [D][Nfc] FWT Timeout
489832 [D][Nfc] FWT Timeout
489833 [E][Iso14443_4aPoller] ATS request failed
489836 [D][Iso14443_4aPoller] Failed to read ATS
489839 [D][Nfc] FWT Timeout
489876 [D][Nfc] FWT Timeout
489877 [E][Iso14443_4aPoller] ATS request failed
489880 [D][Iso14443_4aPoller] Failed to read ATS
489883 [D][Nfc] FWT Timeout
489897 [I][NfcScanner] Detected 1 protocols
490006 [W][ViewPort] ViewPort lockup: see applications/services/gui/view_port.c:245
490064 [I][Elf] Total size of loaded sections: 888
490067 [D][Fap] Library for NfcSupportedCardPlugin, API v. 1 loaded
490112 [I][Elf] Total size of loaded sections: 420
490115 [D][Fap] Library for NfcSupportedCardPlugin, API v. 1 loaded
490170 [I][Elf] Total size of loaded sections: 1804
490173 [D][Fap] Library for NfcSupportedCardPlugin, API v. 1 loaded
490240 [I][Elf] Total size of loaded sections: 3212
490243 [D][Fap] Library for NfcSupportedCardPlugin, API v. 1 loaded
490290 [I][Elf] Total size of loaded sections: 284
490293 [D][Fap] Library for NfcSupportedCardPlugin, API v. 1 loaded
490353 [I][Elf] Total size of loaded sections: 1356
490356 [D][Fap] Library for NfcSupportedCardPlugin, API v. 1 loaded
490402 [I][Elf] Total size of loaded sections: 820
490405 [D][Fap] Library for NfcSupportedCardPlugin, API v. 1 loaded
490454 [I][Elf] Total size of loaded sections: 1844
490457 [D][Fap] Library for NfcSupportedCardPlugin, API v. 1 loaded
490503 [I][Elf] Total size of loaded sections: 548
490506 [D][Fap] Library for NfcSupportedCardPlugin, API v. 1 loaded
490571 [I][Elf] Total size of loaded sections: 1396
490574 [D][Fap] Library for NfcSupportedCardPlugin, API v. 1 loaded
490628 [I][Elf] Total size of loaded sections: 1608
490631 [D][Fap] Library for NfcSupportedCardPlugin, API v. 1 loaded
490680 [I][Elf] Total size of loaded sections: 908
490683 [D][Fap] Library for NfcSupportedCardPlugin, API v. 1 loaded
490746 [I][Elf] Total size of loaded sections: 1212
490749 [D][Fap] Library for NfcSupportedCardPlugin, API v. 1 loaded
490912 [E][Elf] Failed to resolve address for symbol div (hash B886A48)
490916 [E][Elf] Error relocating section '.text'
490918 [I][Elf] Total size of loaded sections: 5044
490978 [I][Elf] Total size of loaded sections: 4568
490981 [D][Fap] Library for NfcSupportedCardPlugin, API v. 1 loaded
491036 [I][Elf] Total size of loaded sections: 4560
491039 [D][Fap] Library for NfcSupportedCardPlugin, API v. 1 loaded
491089 [I][Elf] Total size of loaded sections: 1324
491092 [D][Fap] Library for NfcSupportedCardPlugin, API v. 1 loaded
491151 [I][Elf] Total size of loaded sections: 3276
491154 [D][Fap] Library for NfcSupportedCardPlugin, API v. 1 loaded
491210 [I][Elf] Total size of loaded sections: 1144
491213 [D][Fap] Library for NfcSupportedCardPlugin, API v. 1 loaded
491297 [I][Elf] Total size of loaded sections: 9532
491300 [D][Fap] Library for NfcSupportedCardPlugin, API v. 1 loaded
491358 [I][Elf] Total size of loaded sections: 1956
491361 [D][Fap] Library for NfcSupportedCardPlugin, API v. 1 loaded
491409 [I][Elf] Total size of loaded sections: 368
491412 [D][Fap] Library for NfcSupportedCardPlugin, API v. 1 loaded
491464 [I][Elf] Total size of loaded sections: 1464
491467 [D][Fap] Library for NfcSupportedCardPlugin, API v. 1 loaded
491518 [I][Elf] Total size of loaded sections: 636
491521 [D][Fap] Library for NfcSupportedCardPlugin, API v. 1 loaded
491584 [I][Elf] Total size of loaded sections: 1024
491587 [D][Fap] Library for NfcSupportedCardPlugin, API v. 1 loaded
491591 [D][NfcSupportedCards] Loaded 24 plugins
491608 [D][MfUltralightPoller] Read version success
491611 [D][MfUltralightPoller] NTAG213 detected. Total pages: 45
491614 [D][MfUltralightPoller] Reading signature
491622 [D][MfUltralightPoller] Read signature failed
491624 [D][MfUltralightPoller] Read Failed
491627 [D][Nfc] FWT Timeout
491636 [D][MfUltralightPoller] Read version success
491639 [D][MfUltralightPoller] NTAG213 detected. Total pages: 45
491642 [D][MfUltralightPoller] Reading signature
491650 [D][MfUltralightPoller] Read signature failed
491652 [D][MfUltralightPoller] Read Failed
491655 [D][Nfc] FWT Timeout
491664 [D][MfUltralightPoller] Read version success
491667 [D][MfUltralightPoller] NTAG213 detected. Total pages: 45
491670 [D][MfUltralightPoller] Reading signature
491678 [D][MfUltralightPoller] Read signature failed
491680 [D][MfUltralightPoller] Read Failed
491683 [D][Nfc] FWT Timeout
491692 [D][MfUltralightPoller] Read version success
491695 [D][MfUltralightPoller] NTAG213 detected. Total pages: 45
491698 [D][MfUltralightPoller] Reading signature
491706 [D][MfUltralightPoller] Read signature failed
491708 [D][MfUltralightPoller] Read Failed
491711 [D][Nfc] FWT Timeout
491720 [D][MfUltralightPoller] Read version success
491723 [D][MfUltralightPoller] NTAG213 detected. Total pages: 45
491726 [D][MfUltralightPoller] Reading signature
491734 [D][MfUltralightPoller] Read signature failed
491736 [D][MfUltralightPoller] Read Failed
491739 [D][Nfc] FWT Timeout
491748 [D][MfUltralightPoller] Read version success
491751 [D][MfUltralightPoller] NTAG213 detected. Total pages: 45
491754 [D][MfUltralightPoller] Reading signature
491762 [D][MfUltralightPoller] Read signature failed
491764 [D][MfUltralightPoller] Read Failed
491767 [D][Nfc] FWT Timeout
491776 [D][MfUltralightPoller] Read version success
491779 [D][MfUltralightPoller] NTAG213 detected. Total pages: 45
491782 [D][MfUltralightPoller] Reading signature
491790 [D][MfUltralightPoller] Read signature failed
491792 [D][MfUltralightPoller] Read Failed
491795 [D][Nfc] FWT Timeout
491804 [D][MfUltralightPoller] Read version success
491807 [D][MfUltralightPoller] NTAG213 detected. Total pages: 45
491810 [D][MfUltralightPoller] Reading signature
491818 [D][MfUltralightPoller] Read signature failed
491820 [D][MfUltralightPoller] Read Failed
491823 [D][Nfc] FWT Timeout
491832 [D][MfUltralightPoller] Read version success
491835 [D][MfUltralightPoller] NTAG213 detected. Total pages: 45
491838 [D][MfUltralightPoller] Reading signature
491846 [D][MfUltralightPoller] Read signature failed
491848 [D][MfUltralightPoller] Read Failed
491851 [D][Nfc] FWT Timeout
491860 [D][MfUltralightPoller] Read version success
491863 [D][MfUltralightPoller] NTAG213 detected. Total pages: 45
491866 [D][MfUltralightPoller] Reading signature
491874 [D][MfUltralightPoller] Read signature failed
491876 [D][MfUltralightPoller] Read Failed
491879 [D][Nfc] FWT Timeout
491888 [D][MfUltralightPoller] Read version success
491891 [D][MfUltralightPoller] NTAG213 detected. Total pages: 45
491894 [D][MfUltralightPoller] Reading signature
491902 [D][MfUltralightPoller] Read signature failed
491904 [D][MfUltralightPoller] Read Failed
491907 [D][Nfc] FWT Timeout
491916 [D][MfUltralightPoller] Read version success
491918 [D][MfUltralightPoller] NTAG213 detected. Total pages: 45
491922 [D][MfUltralightPoller] Reading signature
491929 [D][MfUltralightPoller] Read signature failed
491932 [D][MfUltralightPoller] Read Failed
491935 [D][Nfc] FWT Timeout
491944 [D][MfUltralightPoller] Read version success
491947 [D][MfUltralightPoller] NTAG213 detected. Total pages: 45
491950 [D][MfUltralightPoller] Reading signature
491958 [D][MfUltralightPoller] Read signature failed
491960 [D][MfUltralightPoller] Read Failed
491963 [D][Nfc] FWT Timeout
491972 [D][MfUltralightPoller] Read version success
491975 [D][MfUltralightPoller] NTAG213 detected. Total pages: 45
491978 [D][MfUltralightPoller] Reading signature
491986 [D][MfUltralightPoller] Read signature failed
491988 [D][MfUltralightPoller] Read Failed
491991 [D][Nfc] FWT Timeout
```

### Anything else?

**Output from NFC tools:**

_Tag Type: ISO 14443-3A_
NXP - Mifare Ultralight (Ultralight)

_Technologies available_
NfcA, MifareUltralight, NdefFormatable

_Serial number_
04:79:CC:FA:9D:1D:90

_ATQA_
0x0044

_SAK_
0x00

---
*This issue was automatically imported from the upstream Flipper Zero firmware repository.*
