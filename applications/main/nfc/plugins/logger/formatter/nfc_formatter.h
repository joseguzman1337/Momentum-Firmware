#pragma once

#include <furi.h>
#include <nfc/helpers/logger/nfc_trace_data_type.h>
#include <nfc/helpers/logger/transaction/nfc_transaction.h>

#include "nfc_formatter_context.h"
#include "../nfc_logger_formatter_plugin.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef enum {
    NfcLoggerTransactionFilterAll,
    NfcLoggerTransactionFilterPayloadOnly,
} NfcLoggerTransactionFilter;

typedef enum {
    NfcLoggerHistoryLayerFilterAll,
    NfcLoggerHistoryLayerFilterTopProtocolOnly,
} NfcLoggerHistoryLayerFilter;

typedef struct {
    NfcLoggerTransactionFilter transaction_filter;
    NfcLoggerHistoryLayerFilter history_filter;
} NfcLoggerFormatFilter;

#ifdef __cplusplus
}
#endif
