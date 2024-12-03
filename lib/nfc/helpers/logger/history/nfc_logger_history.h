#pragma once

#include "nfc_logger_flags.h"

#include <furi.h>

#ifdef __cplusplus
extern "C" {
#endif

typedef void NfcHistoryData;

typedef struct {
    NfcProtocol protocol;
    uint8_t data_block_size;
    NfcLoggerFlags request_flags;
} FURI_PACKED NfcHistoryItemBase;

typedef struct {
    NfcHistoryItemBase base;
    NfcHistoryData* data;
} FURI_PACKED NfcHistoryItem;

typedef enum {
    NfcLoggerHistoryLayerFilterAll,
    NfcLoggerHistoryLayerFilterTopProtocolOnly,
} NfcLoggerHistoryLayerFilter;

typedef struct NfcHistory NfcHistory;

#ifdef __cplusplus
}
#endif
