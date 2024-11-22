#pragma once

#include <nfc_mode.h>
#include <nfc/protocols/nfc_protocol.h>
#include <furi_hal_nfc.h>

#include <furi.h>

#include "nfc_logger_history.h"

//#include "nfc_transaction_i.h"

//#include <stdint.h>
//#include <stddef.h>

#ifdef __cplusplus
extern "C" {
#endif

typedef struct NfcLogger NfcLogger;

typedef enum {
    NfcLoggerStateDisabled,
    NfcLoggerStateIdle,
    NfcLoggerStateProcessing,
    NfcLoggerStateStopped,
    NfcLoggerStateError
} NfcLoggerState;

NfcLogger* nfc_logger_alloc(void);
void nfc_logger_free(NfcLogger* instance);
void nfc_logger_config(NfcLogger* instance, bool enabled /*Here some other params can be added*/);
void nfc_logger_set_history_size(NfcLogger* instance, uint8_t size);

bool nfc_logger_enabled(NfcLogger* instance);
void nfc_logger_start(NfcLogger* instance, NfcProtocol protocol, NfcMode mode);
void nfc_logger_stop(NfcLogger* instance);

void nfc_logger_transaction_begin(NfcLogger* instance, FuriHalNfcEvent event);
void nfc_logger_transaction_end(NfcLogger* instance);

void nfc_logger_append_data( //nfc_logger_append_request and append_response instead and this move to static
    NfcLogger* instance,
    const uint8_t* data,
    const size_t data_size,
    bool response);

void nfc_logger_append_history(NfcLogger* instance, NfcHistoryItem* history);

#ifdef __cplusplus
}
#endif
