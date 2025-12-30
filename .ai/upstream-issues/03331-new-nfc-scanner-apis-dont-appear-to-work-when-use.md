# Issue #3331: New NFC scanner APIs don't appear to work when used directly

**Original Issue:** [https://github.com/flipperdevices/flipperzero-firmware/issues/3331](https://github.com/flipperdevices/flipperzero-firmware/issues/3331)
**Author:** @str4d
**Created:** 2023-12-31T02:21:08Z
**Labels:** NFC

## Description

### Describe the bug.

I'm attempting to use the new `nfc_scanner_*` APIs in the Flipper Zero SDK.

The thing I'm observing is that the `NfcScanner`'s internal logging shows it gets through the `NfcScannerStateIdle` handler, but never reaches `NfcScannerStateFindChildrenProtocols` (and therefore not `NfcScannerStateComplete` either, so it never calls my callback). But the ostensibly identical sequence of NFC API calls that the built-in `nfc` app uses, works perfectly.

The main difference between my example app and the built-in `nfc` app is that my app's main thread sleeps after starting the scanner, while the built-in `nfc` app's main thread is running the event loop for the view dispatcher.

### Reproduction

1. Place the following files into `applications_user/nfc_scanner`:

```python
App(
    appid="nfc_scanner",
    name="NFC Scanner",
    apptype=FlipperAppType.EXTERNAL,
    targets=["f7"],
    entry_point="nfc_scanner_app",
    stack_size=5 * 1024,
)
```

```cpp
#include <furi.h>
#include <furi_hal.h>

#include <lib/nfc/nfc.h>
#include <nfc/nfc_scanner.h>

#define TAG "NfcScanner"

void nfc_detect_scan_callback(NfcScannerEvent event, void* context) {
    UNUSED(context);

    FURI_LOG_I(TAG, "Scan callback called");
    if(event.type == NfcScannerEventTypeDetected) {
        FURI_LOG_I(TAG, "Detected %d protocols", event.data.protocol_num);
    }
}

int32_t nfc_scanner_app(void* p) {
    UNUSED(p);

    Nfc* nfc = nfc_alloc();

    FURI_LOG_I(TAG, "Scanning NFC cards for 5 seconds...");

    NfcScanner* scanner = nfc_scanner_alloc(nfc);
    nfc_scanner_start(scanner, nfc_detect_scan_callback, NULL);

    furi_delay_us(5000000);

    nfc_scanner_stop(scanner);
    nfc_scanner_free(scanner);

    FURI_LOG_I(TAG, "Finished scanning!");

    nfc_free(nfc);

    return 0;
}
```

2. Compile and run the app on a Flipper Zero.

### Target

f7, firmware version 0.97.1.

### Logs

Running my example app above, I see the following debug logs:
```text
354500679 [I][Loader] Loading /ext/apps/nfc_scanner.fap
354500712 [I][Elf] Total size of loaded sections: 299
354500714 [I][Loader] Loaded in 35ms
354500717 [I][NfcScanner] Scanning NFC cards for 5 seconds...
354500721 [I][AnimationManager] Unload animation 'L1_Tv_128x47'
354500726 [D][NfcScanner] Found 5 base protocols
354506074 [I][NfcScanner] Finished scanning!
354506088 [I][Loader] App returned: 0
354506090 [I][Loader] Application stopped. Free heap: 141968
```

If I instead run the built-in `nfc` app and click "Read", with the same NFC card by the reader, I see:
```text
354700335 [D][NfcScanner] Found 5 base protocols
354700399 [D][Nfc] FWT Timeout
354700424 [D][Nfc] FWT Timeout
354700476 [D][Nfc] FWT Timeout
354700504 [D][Nfc] FWT Timeout
354700519 [D][NfcScanner] Found 4 children
354700576 [D][Nfc] FWT Timeout
354700579 [D][Nfc] FWT Timeout
354700612 [D][Nfc] FWT Timeout
354700646 [D][Iso14443_4aPoller] Read ATS success
354700688 [I][NfcScanner] Detected 1 protocols
354700856 [I][Elf] Total size of loaded sections: 888
354700858 [D][Fap] Library for NfcSupportedCardPlugin, API v. 1 loaded
354700898 [I][Elf] Total size of loaded sections: 420
354700900 [D][Fap] Library for NfcSupportedCardPlugin, API v. 1 loaded
354700941 [I][Elf] Total size of loaded sections: 872
354700944 [D][Fap] Library for NfcSupportedCardPlugin, API v. 1 loaded
354700994 [I][Elf] Total size of loaded sections: 1244
354700996 [D][Fap] Library for NfcSupportedCardPlugin, API v. 1 loaded
354701046 [I][Elf] Total size of loaded sections: 1324
354701049 [D][Fap] Library for NfcSupportedCardPlugin, API v. 1 loaded
354701092 [I][Elf] Total size of loaded sections: 1724
354701094 [D][Fap] Library for NfcSupportedCardPlugin, API v. 1 loaded
354701137 [I][Elf] Total size of loaded sections: 1768
354701140 [D][Fap] Library for NfcSupportedCardPlugin, API v. 1 loaded
354701182 [I][Elf] Total size of loaded sections: 1464
354701186 [D][Fap] Library for NfcSupportedCardPlugin, API v. 1 loaded
354701228 [I][Elf] Total size of loaded sections: 636
354701232 [D][Fap] Library for NfcSupportedCardPlugin, API v. 1 loaded
354701235 [D][NfcSupportedCards] Loaded 9 plugins
354701252 [D][Iso14443_4aPoller] Read ATS success
```

### Anything else?

_No response_

---
*This issue was automatically imported from the upstream Flipper Zero firmware repository.*
