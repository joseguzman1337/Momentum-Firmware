
#include "nfc_formatter.h"

#include "protocols/nfc_protocol_formatters.h"

#include "nfc/helpers/logger/nfc_trace_data_type_i.h"
#include "nfc/helpers/logger/nfc_transaction_data_type_i.h"
#include "nfc/helpers/logger/history/nfc_history_data_type_i.h"

#include "common/nfc_transaction_formatter.h"

#include <nfc_device.h>
#include <nfc/protocols/nfc_protocol.h>

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
    NfcFormatter* instance,
    const char* file_name,
    const NfcTrace* trace,
    FuriString* output) {
    furi_assert(instance);
    furi_assert(file_name);
    furi_assert(trace);
    furi_assert(output);

    instance->protocol = trace->protocol;
    instance->mode = trace->mode;

    furi_string_printf(output, "Trace info\nName: %s\n", file_name);
    furi_string_cat_printf(
        output,
        "Protocol: %s\nMode: %s\nTransaction count: %d\n\n",
        nfc_device_get_protocol_name(trace->protocol),
        trace->mode == NfcModeListener ? "NfcListener" : "NfcPoller",
        trace->transactions_count);

    nfc_format_trace_protocol_layers_description(trace->protocol, output);
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

NfcFormatter* nfc_formatter_alloc() {
    NfcFormatter* instance = malloc(sizeof(NfcFormatter));

    const size_t width[] = {5, 10, 8, 3, 60, 3, 120};
    const char* names[] = {"Id", "Type", "Time", "Src", "Data", "CRC", "Annotation"};
    instance->table_columns_cnt = COUNT_OF(width);
    instance->table = table_alloc(instance->table_columns_cnt, width, names);
    table_set_column_alignment(instance->table, 4, TableColumnDataAlignmentLeft);

    instance->protocol = NfcProtocolInvalid;
    return instance;
}

void nfc_formatter_free(NfcFormatter* instance) {
    furi_assert(instance);
    table_free(instance->table);
    free(instance);
}

void nfc_format_table_header(const NfcFormatter* instance, FuriString* output) {
    furi_assert(instance);
    table_printf_header(instance->table, output);
}

static NfcHistoryCrcStatus
    nfc_history_find_crc_from_chain(const NfcHistoryChain* chain, const NfcMode mode) {
    NfcHistoryCrcStatus status = NfcHistoryCrcNotSet;
    for(size_t i = 0; i < chain->length; i++) {
        NfcProtocol protocol = chain->items[i].base.protocol;
        const NfcProtocolFormatterBase* formatter = nfc_protocol_formatter_get(protocol, mode);
        const NfcHistoryGetCrcStatusCallback crc_callback = formatter->get_crc_status;
        if(!crc_callback) continue;

        status = crc_callback(&chain->items[i].data);
        break;
    }
    return status;
}

static NfcHistoryCrcStatus
    nfc_history_get_crc_status(const NfcHistory* history, const NfcMode mode) {
    NfcHistoryCrcStatus status = NfcHistoryCrcNotSet;
    for(size_t i = 0; i < history->base.chain_count; i++) {
        status = nfc_history_find_crc_from_chain(&history->chains[i], mode);
        if(status != NfcHistoryCrcNotSet) break;
    }
    return status;
}

void nfc_formatter_format(
    NfcFormatter* instance,
    const NfcTransaction* transaction,
    FuriString* output) {
    furi_assert(instance->protocol != NfcProtocolInvalid);

    instance->crc_from_history = nfc_history_get_crc_status(transaction->history, instance->mode);

    ///TODO: This If needs to be removed. nfc_format_transaction must guarantee that all protocols
    //will behave as expected
    if(instance->protocol == NfcProtocolIso14443_3a ||
       instance->protocol == NfcProtocolMfUltralight || instance->protocol == NfcProtocolFelica) {
        nfc_format_transaction(instance, transaction, output);
    } else
        furi_string_printf(output, "NIMP");
}
