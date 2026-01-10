#pragma once

#include <stdint.h>
#include <stdbool.h>
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

/**
 * Perform a blocking HTTP GET over the current usb_eth/lwIP network interface
 * and write the response body to the given file path on Storage.
 *
 * Only plain HTTP ("http://") URLs are supported. HTTPS is not handled by
 * this helper; use a local HTTP proxy on the host side if TLS is required.
 *
 * @param url        Full HTTP URL (e.g. "http://host:port/path").
 * @param dest_path  Absolute storage path (EXT_PATH or SD path).
 * @param timeout_ms Maximum time to wait for the transfer to complete.
 *
 * @return true on success (HTTP 2xx and non-zero payload written), false otherwise.
 */
bool furi_hal_usb_eth_http_download_to_file(const char* url, const char* dest_path, uint32_t timeout_ms);

#ifdef __cplusplus
}
#endif
