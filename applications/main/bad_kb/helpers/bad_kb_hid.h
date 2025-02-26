#pragma once

#ifdef __cplusplus
extern "C" {
#endif

#include <furi.h>
#include <furi_hal.h>

#include "ble_hid_profile.h"

typedef enum {
    BadKbHidInterfaceUsb,
    BadKbHidInterfaceBle,
    BadKbHidInterfaceMAX,
} BadKbHidInterface;

typedef struct {
    BleProfileHidParams ble;
    FuriHalUsbHidConfig usb;
} BadKbHidConfig;

typedef struct {
    void (*adjust_config)(BadKbHidConfig* hid_cfg);
    void* (*init)(BadKbHidConfig* hid_cfg);
    void (*deinit)(void* inst);
    void (*set_state_callback)(void* inst, HidStateCallback cb, void* context);
    bool (*is_connected)(void* inst);

    bool (*kb_press)(void* inst, uint16_t button);
    bool (*kb_release)(void* inst, uint16_t button);
    bool (*mouse_press)(void* inst, uint8_t button);
    bool (*mouse_release)(void* inst, uint8_t button);
    bool (*mouse_scroll)(void* inst, int8_t delta);
    bool (*mouse_move)(void* inst, int8_t dx, int8_t dy);
    bool (*consumer_press)(void* inst, uint16_t button);
    bool (*consumer_release)(void* inst, uint16_t button);
    bool (*release_all)(void* inst);
    uint8_t (*get_led_state)(void* inst);
} BadKbHidApi;

const BadKbHidApi* bad_kb_hid_get_interface(BadKbHidInterface interface);

void bad_kb_hid_ble_remove_pairing(void);

#ifdef __cplusplus
}
#endif
