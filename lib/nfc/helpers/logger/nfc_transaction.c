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

static void nfc_packet_format(NfcPacket* packet, FuriString* output) {
    furi_string_reset(output);
    size_t n = packet->data_size;
    if(packet->data_size >= 3) {
        n = packet->data_size - 2;
    }

    for(size_t i = 0; i < n; i++) {
        furi_string_cat_printf(output, "%02X ", packet->data[i]);
    }

    if(packet->data_size >= 3) {
        furi_string_cat_printf(output, "[ %02X %02X ]", packet->data[n], packet->data[n + 1]);
    }
}

NfcTransactionString* nfc_transaction_string_alloc() {
    NfcTransactionString* transaction = malloc(sizeof(NfcTransactionString));
    FuriString** array = (FuriString**)transaction;
    for(size_t i = 0; i < (sizeof(NfcTransactionString) / sizeof(FuriString*)); i++) {
        array[i] = furi_string_alloc();
    }
    return transaction;
}

void nfc_transaction_string_reset(NfcTransactionString* transaction) {
    FuriString** array = (FuriString**)transaction;
    for(size_t i = 0; i < (sizeof(NfcTransactionString) / sizeof(FuriString*)); i++) {
        furi_string_reset(array[i]);
    }
}

void nfc_transaction_string_free(NfcTransactionString* transaction) {
    furi_assert(transaction);

    FuriString** array = (FuriString**)transaction;
    for(size_t i = 0; i < (sizeof(NfcTransactionString) / sizeof(FuriString*)); i++) {
        furi_string_free(array[i]);
    }
    free(transaction);
}

static const char* nfc_transaction_get_type_name(NfcTransactionType type) {
    switch(type) {
    case NfcTransactionTypeEmpty:
        return "HalNfc";
    case NfcTransactionTypeFlagsOnly:
        return "FlagsOnly";
    case NfcTransactionTypeRequest:
        return "Request";
    case NfcTransactionTypeResponse:
        return "Response";
    case NfcTransactionTypeRequestResponse:
        return "Full";
    default:
        return "Unknown";
    }
}

static void nfc_transaction_format_common(
    NfcTransaction* transaction,
    NfcTransactionType desired_type,
    NfcTransactionString* output) {
    do {
        NfcTransactionHeader* header = &transaction->header;
        uint32_t time = (header->type == NfcTransactionTypeFlagsOnly ||
                         header->type == NfcTransactionTypeEmpty) ?
                            header->time :
                            transaction->request->time;

        if(desired_type != NfcTransactionTypeResponse ||
           header->type != NfcTransactionTypeRequestResponse) {
            furi_string_printf(output->id, "%ld", header->id);
            furi_string_printf(output->type, "%s", nfc_transaction_get_type_name(header->type));
            furi_string_printf(output->src, "RDR");
        } else
            furi_string_printf(output->src, "TAG");

        furi_string_printf(output->time, "%ld", time);

        if((header->type == NfcTransactionTypeRequest ||
            header->type == NfcTransactionTypeRequestResponse) &&
           (desired_type == NfcTransactionTypeRequest)) {
            nfc_packet_format(transaction->request, output->payload);
        }

        if((header->type == NfcTransactionTypeResponse ||
            header->type == NfcTransactionTypeRequestResponse) &&
           (desired_type == NfcTransactionTypeResponse)) {
            nfc_packet_format(transaction->response, output->payload);
        }

        nfc_histroy_format_crc_status(transaction->history, output->crc_status);
    } while(false);
}

void nfc_transaction_format_request(
    NfcTransaction* transaction,
    NfcLoggerHistoryLayerFilter filter,
    NfcTransactionString* output) {
    furi_assert(output);
    furi_assert(transaction);

    nfc_transaction_format_common(transaction, NfcTransactionTypeRequest, output);
    nfc_histroy_format_annotation(
        transaction->history, transaction->header.nfc_event, filter, output->annotation);
}

void nfc_transaction_format_response(NfcTransaction* transaction, NfcTransactionString* output) {
    furi_assert(output);
    furi_assert(transaction);

    nfc_transaction_format_common(transaction, NfcTransactionTypeResponse, output);
}
