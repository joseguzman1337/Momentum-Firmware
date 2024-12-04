
#include "nfc_history_data_formatter.h"
#include "nfc_history_data_formatter_base.h"

#include "nfc_transaction_string.h"

#include "nfc/helpers/logger/nfc_trace_data_type_i.h"
#include "nfc/helpers/logger/nfc_transaction_data_type_i.h"

#include "protocols/iso14443_3a/iso14443_3a_listener_data_formatter.h"
#include "protocols/mf_ultralight/mf_ultralight_data_formatter.h"

#include <nfc_device.h>
#include <nfc/protocols/nfc_protocol.h>

static const NfcHistoryItemDataHandler* formatters[] = {
    [NfcProtocolIso14443_3a] = &iso14443_3a_listener_data_formatter,
    [NfcProtocolMfUltralight] = &mf_ultralight_listener_data_formatter,
};

void nfc_history_data_format(
    NfcProtocol protocol,
    NfcMode mode,
    const NfcHistoryData* data,
    FuriString* output) {
    furi_assert(mode == NfcModeListener);
    if(protocol == NfcProtocolIso14443_3a || protocol == NfcProtocolMfUltralight) {
        const NfcHistoryItemDataHandler* f = formatters[protocol];
        f->format(data, output);
    } else
        furi_string_printf(output, "NIMP");
}

static void
    nfc_format_trace_protocol_layers_description(NfcProtocol trace_protocol, FuriString* output) {
    furi_assert(output);
    furi_assert(trace_protocol < NfcProtocolNum);

    furi_string_cat_printf(output, "Protocol layers:\r\n");

    uint8_t count = 0;
    NfcProtocol* protocols = nfc_protocol_layer_list_alloc(trace_protocol, &count);
    furi_string_cat_printf(output, "L0 - NFC\r\n");
    for(uint8_t i = 0; i < count; i++) {
        furi_string_cat_printf(
            output, "L%d - %s\r\n", i + 1, nfc_device_get_protocol_name(protocols[i]));
    }
    furi_string_cat_printf(output, "\r\n");
    nfc_protocol_layer_list_free(protocols);
}

void nfc_format_trace(
    const NfcFormatter* instance,
    const char* file_name,
    const NfcTrace* trace,
    FuriString* output) {
    furi_assert(instance);
    furi_assert(file_name);
    furi_assert(trace);
    furi_assert(output);

    furi_string_printf(output, "Trace info\nName: %s\n", file_name);
    furi_string_cat_printf(
        output,
        "Protocol: %s\nMode: %s\nTransaction count: %d\n\n",
        nfc_device_get_protocol_name(trace->protocol),
        trace->mode == NfcModeListener ? "NfcListener" : "NfcPoller",
        trace->transactions_count);

    nfc_format_trace_protocol_layers_description(trace->protocol, output);
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

static void nfc_transaction_format_common(
    const NfcTransaction* transaction,
    NfcTransactionType desired_type,
    NfcTransactionString* output) {
    do {
        const NfcTransactionHeader* header = &transaction->header;
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

inline static void nfc_transaction_format_request(
    const NfcTransaction* transaction,
    NfcLoggerHistoryLayerFilter filter,
    NfcTransactionString* output) {
    furi_assert(output);
    furi_assert(transaction);

    nfc_transaction_format_common(transaction, NfcTransactionTypeRequest, output);
    nfc_histroy_format_annotation(
        transaction->history, transaction->header.nfc_event, filter, output->annotation);
}

inline static void nfc_transaction_format_response(
    const NfcTransaction* transaction,
    NfcTransactionString* output) {
    furi_assert(output);
    furi_assert(transaction);

    nfc_transaction_format_common(transaction, NfcTransactionTypeResponse, output);
}

/* static bool rzac_filter_apply(NfcLoggerTransactionFilter filter, NfcTransactionType type) {
    bool result = (filter == NfcLoggerTransactionFilterAll);
    if(filter == NfcLoggerTransactionFilterPayloadOnly &&
       (type == NfcTransactionTypeRequestResponse || type == NfcTransactionTypeRequest ||
        type == NfcTransactionTypeResponse)) {
        result = true;
    }

    return result;
} */

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
            nfc_transaction_format_request(transaction, instance->filter.history_filter, tr_str);
            table_printf_row_array(table, output, (FuriString**)tr_str, count);
        }

        if(transaction->header.type == NfcTransactionTypeResponse ||
           transaction->header.type == NfcTransactionTypeRequestResponse) {
            nfc_transaction_string_reset(tr_str);
            nfc_transaction_format_response(transaction, tr_str);
            table_printf_row_array(table, output, (FuriString**)tr_str, count);
        }
    } while(false);
    nfc_transaction_string_free(tr_str);
}

void nfc_format_table_header(const NfcFormatter* instance, FuriString* output) {
    furi_assert(instance);
    table_printf_header(instance->table, output);
}

NfcFormatter* nfc_formatter_alloc() {
    NfcFormatter* instance = malloc(sizeof(NfcFormatter));

    const size_t width[] = {5, 10, 8, 3, 60, 3, 120};
    const char* names[] = {"Id", "Type", "Time", "Src", "Data", "CRC", "Annotation"};
    instance->table_columns_cnt = COUNT_OF(width);
    instance->table = table_alloc(instance->table_columns_cnt, width, names);
    table_set_column_alignment(instance->table, 4, TableColumnDataAlignmentLeft);

    return instance;
}

void nfc_formatter_free(NfcFormatter* instance) {
    furi_assert(instance);
    table_free(instance->table);
    free(instance);
}
