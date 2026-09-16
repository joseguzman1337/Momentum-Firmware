#pragma once

#include <furi.h>

#define RECORD_USB_ETHERNET "usb_ethernet"

typedef bool (*UsbEthernetPingCallback)(
    void* context,
    const char* host,
    uint32_t count,
    uint32_t timeout_ms);
typedef bool (*UsbEthernetHttpCallback)(
    void* context,
    const char* url,
    const char* dest_path,
    uint32_t timeout_ms);
typedef bool (*UsbEthernetStatusCallback)(void* context);

typedef struct {
    FuriMutex* mutex;
    void* context;
    UsbEthernetPingCallback ping;
    UsbEthernetHttpCallback http_download;
    UsbEthernetStatusCallback status;
    uint32_t active_calls;
} UsbEthernetBroker;

static inline void usb_ethernet_broker_register(
    UsbEthernetBroker* broker,
    void* context,
    UsbEthernetPingCallback ping,
    UsbEthernetHttpCallback http_download,
    UsbEthernetStatusCallback status) {
    furi_check(furi_mutex_acquire(broker->mutex, FuriWaitForever) == FuriStatusOk);
    furi_check(!broker->context && !broker->active_calls);
    broker->context = context;
    broker->ping = ping;
    broker->http_download = http_download;
    broker->status = status;
    furi_check(furi_mutex_release(broker->mutex) == FuriStatusOk);
}

static inline void usb_ethernet_broker_unregister(UsbEthernetBroker* broker, void* context) {
    furi_check(furi_mutex_acquire(broker->mutex, FuriWaitForever) == FuriStatusOk);
    furi_check(broker->context == context);
    broker->context = NULL;
    broker->ping = NULL;
    broker->http_download = NULL;
    broker->status = NULL;
    furi_check(furi_mutex_release(broker->mutex) == FuriStatusOk);

    while(true) {
        furi_check(furi_mutex_acquire(broker->mutex, FuriWaitForever) == FuriStatusOk);
        const bool idle = broker->active_calls == 0;
        furi_check(furi_mutex_release(broker->mutex) == FuriStatusOk);
        if(idle) break;
        furi_delay_tick(1);
    }
}

static inline bool usb_ethernet_broker_ping(
    UsbEthernetBroker* broker,
    const char* host,
    uint32_t count,
    uint32_t timeout_ms) {
    furi_check(furi_mutex_acquire(broker->mutex, FuriWaitForever) == FuriStatusOk);
    UsbEthernetPingCallback callback = broker->ping;
    void* context = broker->context;
    if(callback) broker->active_calls++;
    furi_check(furi_mutex_release(broker->mutex) == FuriStatusOk);

    const bool result = callback ? callback(context, host, count, timeout_ms) : false;
    if(callback) {
        furi_check(furi_mutex_acquire(broker->mutex, FuriWaitForever) == FuriStatusOk);
        furi_check(broker->active_calls);
        broker->active_calls--;
        furi_check(furi_mutex_release(broker->mutex) == FuriStatusOk);
    }
    return result;
}
