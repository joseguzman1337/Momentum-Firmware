#pragma once

#include <furi.h>
#include <nfc.h>

#ifdef __cplusplus
extern "C" {
#endif

typedef void (*NfcHistoryItemDataFormatCallback)(const NfcHistoryData* data, FuriString* output);

typedef struct {
    uint8_t data_size;
    NfcHistoryItemDataFormatCallback format;
} NfcHistoryItemDataHandler;

#ifdef __cplusplus
}
#endif
