#pragma once

#include "history/nfc_history.h"

#include <furi.h>
#include <furi_hal_nfc.h>

#include <nfc/protocols/nfc_protocol.h>

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
