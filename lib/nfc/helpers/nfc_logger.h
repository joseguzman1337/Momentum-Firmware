#pragma once

#include <nfc_mode.h>
#include <nfc/protocols/nfc_protocol.h>

#include <stdint.h>
#include <stddef.h>
/*#include <stdlib.h> */

#ifdef __cplusplus
extern "C" {
#endif

typedef struct NfcLogger NfcLogger;

NfcLogger* nfc_logger_alloc(void);
void nfc_logger_free(NfcLogger* instance);
void nfc_logger_config(NfcLogger* instance, bool enabled /*Here some other params can be added*/);

void nfc_logger_start(NfcLogger* instance, NfcProtocol protocol, NfcMode mode);
void nfc_logger_stop(NfcLogger* instance);

void nfc_logger_transaction_begin(NfcLogger* instance);
void nfc_logger_transaction_end(NfcLogger* instance);
void nfc_logger_transaction_append(
    NfcLogger* instance,
    const uint8_t* data,
    const size_t data_size,
    bool response);

#ifdef __cplusplus
}
#endif
