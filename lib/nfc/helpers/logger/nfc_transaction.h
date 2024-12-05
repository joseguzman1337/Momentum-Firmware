#pragma once

///TODO: temporary added headers
#include <storage/storage.h>
#include <stream/file_stream.h>
#include <toolbox/path.h>
#include <furi_hal_nfc.h>

#include "history/nfc_logger_history.h"
#include "history/nfc_logger_flags.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef enum {
    NfcTransactionTypeEmpty,
    NfcTransactionTypeFlagsOnly,
    NfcTransactionTypeRequest,
    NfcTransactionTypeResponse, //TODO: remove this, because NFC cannot send response without request
    NfcTransactionTypeRequestResponse,
} NfcTransactionType;

typedef struct NfcTransaction NfcTransaction;

///TODO: Think of moving major part of these functions to _i.h header and expose them only for logger.c under the hood
///without putting them into api

/* NfcTransaction*
    nfc_transaction_alloc(uint32_t id, FuriHalNfcEvent event, uint8_t history_size_bytes); */
NfcTransaction* nfc_transaction_alloc(
    uint32_t id,
    FuriHalNfcEvent event,
    uint8_t history_size_bytes,
    uint8_t max_chain_count);

void nfc_transaction_free(NfcTransaction* instance);
NfcTransactionType nfc_transaction_get_type(const NfcTransaction* instance);
uint32_t nfc_transaction_get_id(const NfcTransaction* instance);

void nfc_transaction_append(
    NfcTransaction* transaction,
    const uint8_t* data,
    const size_t data_size,
    bool response);
void nfc_transaction_append_history(NfcTransaction* transaction, NfcHistoryItem* item);
void nfc_transaction_save_to_file(File* file, const NfcTransaction* transaction);

bool nfc_transaction_read(Stream* stream, NfcTransaction** transaction_ptr);

#ifdef __cplusplus
}
#endif
