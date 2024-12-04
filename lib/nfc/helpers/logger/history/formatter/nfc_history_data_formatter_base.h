#pragma once

#include <furi.h>
#include <nfc.h>
#include "nfc/helpers/logger/nfc_packet_data_type_i.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef void (*NfcHistoryItemDataFormatCallback)(const NfcHistoryData* data, FuriString* output);
typedef void (*NfcFormatterCallbackFormatPacket)(const NfcPacket* pack, FuriString* output);

typedef struct {
    uint8_t data_size;
    NfcHistoryItemDataFormatCallback format;
} NfcHistoryItemDataHandler;

#ifdef __cplusplus
}
#endif
