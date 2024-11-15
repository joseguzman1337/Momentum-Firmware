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

typedef struct {
    uint32_t time;
    uint32_t flags;
    size_t data_size;
    uint8_t* data;
} NfcPacketString;

typedef struct {
    FuriString* id;
    FuriString* type;
    FuriString* nfc_event;
    FuriString* time;
    FuriString* src;
    FuriString* request;
    FuriString* response;
    FuriString* annotation;
} NfcTransactionString;

NfcTransaction*
    nfc_transaction_alloc(uint32_t id, FuriHalNfcEvent event, uint8_t history_max_size);
void nfc_transaction_free(NfcTransaction* instance);
uint8_t nfc_transaction_get_history_count(NfcTransaction* instance);
NfcTransactionType nfc_transaction_get_type(const NfcTransaction* instance);
uint32_t nfc_transaction_get_id(const NfcTransaction* instance);

void nfc_transaction_append(
    NfcTransaction* transaction,
    const uint8_t* data,
    const size_t data_size,
    bool response);
void nfc_transaction_append_history(NfcTransaction* transaction, NfcLoggerHistory* history);
void nfc_transaction_save_to_file(File* file, const NfcTransaction* transaction);

bool nfc_transaction_read(Stream* stream, NfcTransaction** transaction_ptr);
void nfc_transaction_format(NfcTransaction* transaction, NfcTransactionString* output);
NfcTransactionString* nfc_transaction_string_alloc(void);
void nfc_transaction_string_free(NfcTransactionString* transaction);
void nfc_transaction_string_reset(NfcTransactionString* transaction);

#ifdef __cplusplus
}
#endif
