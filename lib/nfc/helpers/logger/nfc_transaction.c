#include "nfc_logger_i.h"
#include "nfc_transaction_i.h"

#define TAG "NfcTransaction"

static NfcTransaction* nfc_transaction_alloc_empty() {
    return malloc(sizeof(NfcTransaction));
}

NfcTransaction* nfc_transaction_alloc(
    uint32_t id,
    FuriHalNfcEvent event,
    uint8_t history_size_bytes,
    uint8_t max_chain_count) {
    NfcTransaction* t = nfc_transaction_alloc_empty(); //malloc(sizeof(NfcTransaction));
    t->header.type = NfcTransactionTypeEmpty;
    t->header.id = id;
    t->header.nfc_event = event;
    t->header.time = furi_get_tick();
    t->history = nfc_history_alloc(history_size_bytes, max_chain_count);
    return t;
}

void nfc_transaction_free(NfcTransaction* instance) {
    furi_assert(instance);

    // FURI_LOG_D(TAG, "Free_tr: %ld", instance->id);

    if(instance->request) {
        if(instance->request->data) free(instance->request->data);
        free(instance->request);
    }

    if(instance->response) {
        if(instance->response->data) free(instance->response->data);
        free(instance->response);
    }

    nfc_history_free(instance->history);
    free(instance);
}

static NfcPacket* nfc_logger_get_packet(NfcTransaction* transaction, bool response) {
    furi_assert(transaction);

    NfcPacket* p;
    if(response) {
        if(!transaction->response) transaction->response = malloc(sizeof(NfcPacket));
        transaction->header.type = transaction->header.type == NfcTransactionTypeRequest ?
                                       NfcTransactionTypeRequestResponse :
                                       NfcTransactionTypeResponse;
        p = transaction->response;
    } else {
        if(!transaction->request) transaction->request = malloc(sizeof(NfcPacket));
        transaction->header.type = NfcTransactionTypeRequest;
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
    //  FURI_LOG_D(
    //      TAG, "Append_tr: %ld size: %d type: %02X", transaction->id, data_size, transaction->header.type);

    p->time = furi_get_tick();
    p->data_size = data_size;
    p->data = malloc(data_size);
    memcpy(p->data, data, data_size);
}

void nfc_transaction_append_history(NfcTransaction* transaction, NfcHistoryItem* item) {
    furi_assert(transaction);

    // FURI_LOG_D(TAG, "Add history: %ld", transaction->id);
    if(transaction->header.type == NfcTransactionTypeEmpty) {
        transaction->header.type = NfcTransactionTypeFlagsOnly;
    }
    nfc_history_append(transaction->history, item);
}

NfcTransactionType nfc_transaction_get_type(const NfcTransaction* instance) {
    furi_assert(instance);
    return instance->header.type;
}

uint32_t nfc_transaction_get_id(const NfcTransaction* instance) {
    furi_assert(instance);
    return instance->header.id;
}

static void nfc_logger_save_packet(File* file, NfcPacket* packet) {
    if(packet) {
        storage_file_write(file, &packet->time, sizeof(uint32_t) * 2 + sizeof(size_t));
        storage_file_write(file, packet->data, packet->data_size);
    }
}

void nfc_transaction_save_to_file(File* file, const NfcTransaction* transaction) {
    //  FURI_LOG_D(TAG, "Save_tr: %ld", transaction->id);
    storage_file_write(file, &(transaction->header), sizeof(NfcTransactionHeader));

    if(transaction->header.type == NfcTransactionTypeRequest ||
       transaction->header.type == NfcTransactionTypeRequestResponse)
        nfc_logger_save_packet(file, transaction->request);

    if(transaction->header.type == NfcTransactionTypeResponse ||
       transaction->header.type == NfcTransactionTypeRequestResponse)
        nfc_logger_save_packet(file, transaction->response);

    nfc_history_save(file, transaction->history);
}

///TODO: rework this function so it will apply filter by itself and simply  skip
///transactions which don't match to filter values;
bool nfc_transaction_read(Stream* stream, NfcTransaction** transaction_ptr) {
    furi_assert(stream);
    furi_assert(transaction_ptr);

    bool result = false;
    NfcTransaction* transaction = nfc_transaction_alloc_empty();
    do {
        //storage_file_read(file, transaction, sizeof(NfcTransactionHeader));
        size_t bytes_read =
            stream_read(stream, (uint8_t*)transaction, sizeof(NfcTransactionHeader));
        if(bytes_read != sizeof(NfcTransactionHeader)) {
            FURI_LOG_E(TAG, "Unable to read transaction from file");
            break;
        }

        if(transaction->header.type == NfcTransactionTypeRequest ||
           transaction->header.type == NfcTransactionTypeRequestResponse) {
            transaction->request = malloc(sizeof(NfcPacket));
            stream_read(stream, (uint8_t*)transaction->request, sizeof(uint32_t) * 3);

            transaction->request->data = malloc(transaction->request->data_size);
            stream_read(stream, transaction->request->data, transaction->request->data_size);
            //storage_file_read(file, transaction->request->data, transaction->request->data_size);
        }

        if(transaction->header.type == NfcTransactionTypeResponse ||
           transaction->header.type == NfcTransactionTypeRequestResponse) {
            transaction->response = malloc(sizeof(NfcPacket));
            stream_read(stream, (uint8_t*)transaction->response, sizeof(uint32_t) * 3);
            //storage_file_read(file, transaction->response, sizeof(uint32_t) * 3);

            transaction->response->data = malloc(transaction->response->data_size);
            stream_read(stream, transaction->response->data, transaction->response->data_size);
            //storage_file_read(file, transaction->response->data, transaction->response->data_size);
        }

        if(!nfc_history_load(stream, &transaction->history)) break;

        result = true;
        *transaction_ptr = transaction;
    } while(false);

    if(!result) nfc_transaction_free(transaction);

    return result;
}