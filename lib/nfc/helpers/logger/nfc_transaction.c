#include "nfc_logger_i.h"
#include "nfc_transaction_i.h"

#define TAG "NfcTransaction"
//----------------------------------------------------------------------------------------------------------
//NfcTransaction handlers
NfcTransaction* nfc_transaction_alloc(uint32_t id, uint8_t history_max_size) {
    NfcTransaction* t = malloc(sizeof(NfcTransaction));
    t->type = NfcTransactionTypeEmpty;
    t->id = id;
    t->history_count = 0;
    t->history = malloc(sizeof(NfcLoggerHistory) * history_max_size);
    return t;
} */

static NfcTransaction* nfc_transaction_alloc_empty() {
    return malloc(sizeof(NfcTransaction));
}

NfcTransaction*
    nfc_transaction_alloc(uint32_t id, FuriHalNfcEvent event, uint8_t history_max_size) {
    NfcTransaction* t = nfc_transaction_alloc_empty(); //malloc(sizeof(NfcTransaction));
    t->header.type = NfcTransactionTypeEmpty;
    t->header.id = id;
    t->header.history_count = 0;
    t->header.nfc_event = event;
    t->header.time = furi_get_tick();
    t->history = malloc(sizeof(NfcLoggerHistory) * history_max_size);
    return t;
}

void nfc_transaction_free(NfcTransaction* instance) {
    furi_assert(instance);

    FURI_LOG_D(TAG, "Free_tr: %ld", instance->id);

    if(instance->request) {
        if(instance->request->data) free(instance->request->data);
        free(instance->request);
    }

    if(instance->response) {
        if(instance->response->data) free(instance->response->data);
        free(instance->response);
    }

    free(instance->history);
    free(instance);
}

static NfcPacket* nfc_logger_get_packet(NfcTransaction* transaction, bool response) {
    furi_assert(transaction);

    NfcPacket* p;
    if(response) {
        if(!transaction->response) transaction->response = malloc(sizeof(NfcPacket));
        transaction->type = transaction->type == NfcTransactionTypeRequest ?
                                NfcTransactionTypeRequestResponse :
                                NfcTransactionTypeResponse;
        p = transaction->response;
    } else {
        if(!transaction->request) transaction->request = malloc(sizeof(NfcPacket));
        transaction->type = NfcTransactionTypeRequest;
        p = transaction->request;
    }
    return p;
}

void nfc_transaction_append(
    NfcTransaction* transaction,
    const uint8_t* data,
    const size_t data_size,
    bool response) {
    furi_assert(transaction);
    furi_assert(data);
    furi_assert(data_size > 0);

    NfcPacket* p = nfc_logger_get_packet(transaction, response);
    FURI_LOG_D(
        TAG, "Append_tr: %ld size: %d type: %02X", transaction->id, data_size, transaction->type);

    p->time = furi_get_tick();
    p->data_size = data_size;
    p->data = malloc(data_size);
    memcpy(p->data, data, data_size);
}

void nfc_transaction_append_history(NfcTransaction* transaction, NfcLoggerHistory* history) {
    furi_assert(transaction);

    FURI_LOG_D(TAG, "Add history: %ld", transaction->id);
    transaction->history[transaction->history_count++] = *history;
}

uint8_t nfc_transaction_get_history_count(NfcTransaction* instance) {
    furi_assert(instance);
    return instance->history_count;
}

NfcTransactionType nfc_transaction_get_type(const NfcTransaction* instance) {
    furi_assert(instance);
    return instance->type;
}

static void nfc_logger_save_packet(File* file, NfcPacket* packet) {
    if(packet) {
        storage_file_write(file, &packet->time, sizeof(uint32_t) * 2 + sizeof(size_t));
        storage_file_write(file, packet->data, packet->data_size);
    }
}

void nfc_transaction_save_to_file(File* file, const NfcTransaction* transaction) {
    FURI_LOG_D(TAG, "Save_tr: %ld", transaction->id);
    storage_file_write(
        file, &(transaction->id), sizeof(uint32_t) + sizeof(NfcTransactionType) + sizeof(uint8_t));
    nfc_logger_save_packet(file, transaction->request);
    nfc_logger_save_packet(file, transaction->response);
    //storage_file_write(f, &(ptr->time), sizeof(uint32_t));
    storage_file_write(
        file, transaction->history, transaction->history_count * sizeof(NfcLoggerHistory));
}
