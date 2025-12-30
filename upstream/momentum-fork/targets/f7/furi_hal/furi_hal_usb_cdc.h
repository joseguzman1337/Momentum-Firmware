#pragma once

#include <stdint.h>
#include <furi_hal_usb.h>
#include "usb_cdc.h"

#define CDC_DATA_SZ 64

#ifdef __cplusplus
extern "C" {
#endif

typedef enum {
    CdcStateDisconnected,
    CdcStateConnected,
} CdcState;

typedef enum {
    CdcCtrlLineDTR = (1 << 0),
    CdcCtrlLineRTS = (1 << 1),
} CdcCtrlLine;

typedef struct {
    void (*tx_ep_callback)(void* context);
    void (*rx_ep_callback)(void* context);
    void (*state_callback)(void* context, CdcState state);
    void (*ctrl_line_callback)(void* context, CdcCtrlLine ctrl_lines);
    void (*config_callback)(void* context, struct usb_cdc_line_coding* config);
} CdcCallbacks;

void furi_hal_cdc_set_callbacks(uint8_t if_num, CdcCallbacks* cb, void* context);

struct usb_cdc_line_coding* furi_hal_cdc_get_port_settings(uint8_t if_num);

uint8_t furi_hal_cdc_get_ctrl_line_state(uint8_t if_num);

void furi_hal_cdc_send(uint8_t if_num, uint8_t* buf, uint16_t len);

int32_t furi_hal_cdc_receive(uint8_t if_num, uint8_t* buf, uint16_t max_len);

// Ethernet Extension
extern FuriHalUsbInterface usb_cdc_ecm;

typedef void (*FuriHalUsbNetworkReceiveCallback)(uint8_t* buffer, uint16_t len, void* context);

void furi_hal_usb_ethernet_set_received_callback(
    FuriHalUsbNetworkReceiveCallback callback,
    void* context);
void furi_hal_usb_ethernet_send(uint8_t* buffer, uint16_t len);
void furi_hal_usb_ethernet_get_mac(uint8_t* mac);

#ifdef __cplusplus
}
#endif
