
#pragma once

#include <furi.h>
#include <nfc_mode.h>
#include <nfc/protocols/nfc_protocol.h>

#ifdef __cplusplus
extern "C" {
#endif

typedef void NfcHistoryData;

typedef struct {
    NfcProtocol protocol;
    uint8_t data_block_size;
} FURI_PACKED NfcHistoryItemBase;

typedef struct {
    NfcHistoryItemBase base;
    NfcHistoryData* data;
} FURI_PACKED NfcHistoryItem;

typedef struct {
    NfcHistoryItemBase base;
    uint8_t data[];
} FURI_PACKED NfcHistoryItemInternal;

#ifdef __cplusplus
}
#endif
