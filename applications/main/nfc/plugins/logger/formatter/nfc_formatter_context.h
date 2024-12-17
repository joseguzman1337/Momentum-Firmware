#pragma once

#include "helpers/table.h"
#include "helpers/nfc_transaction_string.h"

#include <nfc_mode.h>
#include <nfc/protocols/nfc_protocol.h>

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
