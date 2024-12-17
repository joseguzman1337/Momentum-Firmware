#include "nfc_transaction_formatter.h"
#include "nfc_history_formatter.h"

#include <nfc/helpers/logger/transaction/nfc_transaction_data_type.h>

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

static const char* nfc_history_crc_status_message[] = {
    [NfcHistoryCrcNotSet] = "",
    [NfcHistoryCrcOk] = "OK",
    [NfcHistoryCrcBad] = "KO",
};

static void
    nfc_transaction_format_crc_status(const NfcFormatter* formatter, FuriString* crc_status_str) {
    //NfcHistoryCrcStatus status = nfc_history_find_crc_status(history);
    furi_string_printf(
        crc_status_str, nfc_history_crc_status_message[formatter->crc_from_history]);
}

static void
    nfc_packet_format_without_crc(const uint8_t* data, const size_t data_size, FuriString* output) {
    for(size_t i = 0; i < data_size; i++) {
        furi_string_cat_printf(output, "%02X ", data[i]);
    }
}

static void nfc_packet_format_with_crc(
    NfcHistoryCrcStatus crc_status,
    NfcPacket* packet,
    FuriString* output) {
    size_t n = packet->data_size;

    if((packet->data_size >= 3) && (crc_status != NfcHistoryCrcNotSet)) {
        n = packet->data_size - 2;
    }

    nfc_packet_format_without_crc(packet->data, n, output);

    if((packet->data_size >= 3) && (crc_status != NfcHistoryCrcNotSet)) {
        const char* format = (crc_status == NfcHistoryCrcOk) ? "[ %02X %02X ]" : "![ %02X %02X ]";
        furi_string_cat_printf(output, format, packet->data[n], packet->data[n + 1]);
    }
}

static void nfc_packet_format(
    const NfcFormatter* instance,
    NfcPacket* packet,
    FuriString* output,
    bool request) {
    furi_string_reset(output);

    NfcHistoryCrcStatus crc_status = NfcHistoryCrcOk;
    if((instance->mode == NfcModeListener && request) ||
       (instance->mode == NfcModePoller && !request)) {
        crc_status = instance->crc_from_history;
    }
    nfc_packet_format_with_crc(crc_status, packet, output);
}

static void nfc_transaction_format_common(
    const NfcFormatter* instance,
    const NfcTransaction* transaction,
    NfcTransactionType desired_type,
    NfcTransactionString* output) {
    do {
        const NfcTransactionHeader* header = &transaction->header;
        uint32_t time = (header->type == NfcTransactionTypeFlagsOnly ||
                         header->type == NfcTransactionTypeEmpty) ?
                            header->start_time :
                            transaction->request->time;

        if(desired_type != NfcTransactionTypeResponse ||
           header->type != NfcTransactionTypeRequestResponse) {
            furi_string_printf(output->id, "%ld", header->id);
            furi_string_printf(output->type, "%s", nfc_transaction_get_type_name(header->type));
            furi_string_printf(output->src, "RDR");
        } else
            furi_string_printf(output->src, "TAG");

        furi_string_printf(output->time, "%lu", time);

        if((header->type == NfcTransactionTypeRequest ||
            header->type == NfcTransactionTypeRequestResponse) &&
           (desired_type == NfcTransactionTypeRequest)) {
            nfc_packet_format(instance, transaction->request, output->payload, true);
        }

        if((header->type == NfcTransactionTypeResponse ||
            header->type == NfcTransactionTypeRequestResponse) &&
           (desired_type == NfcTransactionTypeResponse)) {
            nfc_packet_format(instance, transaction->response, output->payload, false);
        }

        nfc_transaction_format_crc_status(instance, output->crc_status);
    } while(false);
}

inline static void nfc_transaction_format_request(
    const NfcFormatter* instance,
    const NfcTransaction* transaction,
    //NfcLoggerHistoryLayerFilter filter,
    NfcTransactionString* output) {
    furi_assert(output);
    furi_assert(transaction);
    // UNUSED(filter);

    nfc_transaction_format_common(instance, transaction, NfcTransactionTypeRequest, output);
    nfc_histroy_format_annotation(
        instance,
        transaction->request,
        transaction->history,
        transaction->header.nfc_event,
        output->annotation);
}

inline static void nfc_transaction_format_response(
    const NfcFormatter* instance,
    const NfcTransaction* transaction,
    NfcTransactionString* output) {
    furi_assert(output);
    furi_assert(transaction);

    nfc_transaction_format_common(instance, transaction, NfcTransactionTypeResponse, output);
}

void nfc_format_transaction(
    const NfcFormatter* instance,
    const NfcTransaction* transaction,
    FuriString* output) {
    furi_assert(instance);
    furi_assert(transaction);
    furi_assert(output);
    NfcTransactionString* tr_str = nfc_transaction_string_alloc();

    do {
        // if(!rzac_filter_apply(filter->transaction_filter, type)) break;

        Table* table = instance->table;
        const uint8_t count = instance->table_columns_cnt;

        if(transaction->header.type != NfcTransactionTypeResponse) {
            nfc_transaction_string_reset(tr_str);
            nfc_transaction_format_request(
                instance, transaction, /* instance->filter.history_filter, */ tr_str);
            table_printf_row_array(table, output, (FuriString**)tr_str, count);
        }

        if(transaction->header.type == NfcTransactionTypeResponse ||
           transaction->header.type == NfcTransactionTypeRequestResponse) {
            nfc_transaction_string_reset(tr_str);
            nfc_transaction_format_response(instance, transaction, tr_str);
            table_printf_row_array(table, output, (FuriString**)tr_str, count);
        }
    } while(false);
    nfc_transaction_string_free(tr_str);
}
