#pragma once

#include <furi.h>
#include <furi_hal_nfc.h>
#include <stream/file_stream.h>

#include <nfc/protocols/nfc_protocol.h>
#include "transaction/nfc_transaction.h"
#include "history/nfc_history.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef struct NfcLogger NfcLogger;

typedef enum {
    NfcLoggerTransactionFilterAll,
    NfcLoggerTransactionFilterPayloadOnly,
} NfcLoggerTransactionFilter;

typedef struct {
    NfcLoggerTransactionFilter transaction_filter;
    NfcLoggerHistoryLayerFilter history_filter;
} NfcLoggerFormatFilter;

typedef enum {
    NfcLoggerStateDisabled,
    NfcLoggerStateIdle,
    NfcLoggerStateProcessing,
    NfcLoggerStateStopped,
    NfcLoggerStateError
} NfcLoggerState;

void nfc_logger_config(NfcLogger* instance, bool enabled, const NfcLoggerFormatFilter* filter);

#ifdef __cplusplus
}
#endif
