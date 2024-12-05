#pragma once

#include <nfc/protocols/nfc_protocol.h>
#include <furi_hal_nfc.h>

#include <furi.h>

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

NfcLogger* nfc_logger_alloc(void);
void nfc_logger_free(NfcLogger* instance);
void nfc_logger_config(NfcLogger* instance, bool enabled, const NfcLoggerFormatFilter* filter);
void nfc_logger_set_protocol(NfcLogger* instance, NfcProtocol protocol);

bool nfc_logger_enabled(NfcLogger* instance);
void nfc_logger_start(NfcLogger* instance, NfcMode mode);
void nfc_logger_stop(NfcLogger* instance);

void nfc_logger_transaction_begin(NfcLogger* instance, FuriHalNfcEvent event);
void nfc_logger_transaction_end(NfcLogger* instance);

void nfc_logger_append_request(NfcLogger* instance, const uint8_t* data, const size_t data_size);
void nfc_logger_append_response(NfcLogger* instance, const uint8_t* data, const size_t data_size);
void nfc_logger_append_history(NfcLogger* instance, NfcHistoryItem* history);

#ifdef __cplusplus
}
#endif
