#pragma once

#ifdef __cplusplus
extern "C" {
#endif

typedef enum {
    NfcTransactionTypeEmpty,
    NfcTransactionTypeFlagsOnly,
    NfcTransactionTypeRequest,
    NfcTransactionTypeResponse,
    NfcTransactionTypeRequestResponse,
} NfcTransactionType;

typedef struct NfcTransaction NfcTransaction;

NfcTransaction* nfc_transaction_alloc(uint32_t id, uint8_t history_max_size);
void nfc_transaction_free(NfcTransaction* instance);
uint8_t nfc_transaction_get_history_count(NfcTransaction* instance);
NfcTransactionType nfc_transaction_get_type(const NfcTransaction* instance);

void nfc_transaction_append(
    NfcTransaction* transaction,
    const uint8_t* data,
    const size_t data_size,
    bool response);
void nfc_transaction_append_history(NfcTransaction* transaction, NfcLoggerHistory* history);
void nfc_transaction_save_to_file(File* file, const NfcTransaction* transaction);

#ifdef __cplusplus
}
#endif
