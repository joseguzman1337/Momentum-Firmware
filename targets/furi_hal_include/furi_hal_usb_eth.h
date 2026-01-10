#pragma once

#include <stdint.h>
#include <furi_hal_usb.h>

#ifdef __cplusplus
extern "C" {
#endif

typedef struct FuriHalUsbEthConfig FuriHalUsbEthConfig;

struct FuriHalUsbEthConfig {
    uint16_t vid;
    uint16_t pid;
    char manuf[32];
    char product[32];
};

extern FuriHalUsbInterface usb_eth;

#ifdef __cplusplus
}
#endif
