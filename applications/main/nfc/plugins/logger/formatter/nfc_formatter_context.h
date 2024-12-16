#pragma once

#include <furi.h>
#include <nfc_mode.h>
#include <nfc/protocols/nfc_protocol.h>
#include "table.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef enum {
    NfcHistoryCrcNotSet,
    NfcHistoryCrcOk,
    NfcHistoryCrcBad
} NfcHistoryCrcStatus;

typedef struct {
    NfcProtocol protocol;
    NfcMode mode;
    uint8_t table_columns_cnt;
    NfcHistoryCrcStatus crc_from_history;
    // NfcLoggerFormatFilter filter;
    Table* table;
} NfcFormatter;

#ifdef __cplusplus
}
#endif
