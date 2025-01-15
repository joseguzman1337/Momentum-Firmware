#include "nfc_history_formatter.h"
#include "../protocols/nfc_hal/nfc_hal_formatter.h"
#include "../protocols/nfc_protocol_formatters.h"
#include <nfc/helpers/logger/history/nfc_history_chain_data_type.h>

void nfc_histroy_format_annotation(
    const NfcFormatter* instance,
    const NfcPacket* request,
    const NfcHistory* history,
    const FuriHalNfcEvent nfc_event,
    FuriString* annotation) {
    furi_assert(instance);
    furi_assert(annotation);

    const NfcLoggerHistoryLayerFilter filter = instance->config->history_filter;

    FuriString* layer_parsed_str = furi_string_alloc();
    if(filter == NfcLoggerHistoryLayerFilterAll) {
        nfc_hal_data_format_hal_event_type(nfc_event, layer_parsed_str);
        furi_string_printf(annotation, "L0(%s)", furi_string_get_cstr(layer_parsed_str));
    }

    for(size_t i = 0; i < history->base.chain_count; i++) {
        for(size_t j = 0; j < history->chains[i].length; j++) {
            furi_string_reset(layer_parsed_str);
            const NfcHistoryItem* item = &(history->chains[i].items[j]);

            if((filter == NfcLoggerHistoryLayerFilterTopProtocol ||
                filter == NfcLoggerHistoryLayerFilterTopProtocolSimplified) &&
               item->base.protocol != instance->protocol)
                continue;

            const NfcProtocolFormatterBase* protocol_formatter =
                nfc_protocol_formatter_get(item->base.protocol, instance->mode);
            if(!protocol_formatter) break;

            if(filter == NfcLoggerHistoryLayerFilterAll ||
               filter == NfcLoggerHistoryLayerFilterTopProtocol) {
                protocol_formatter->format_history(request, &item->data, layer_parsed_str);

                const char* format =
                    (filter == NfcLoggerHistoryLayerFilterTopProtocol) ? "L%d(%s)" : "->L%d(%s)";
                furi_string_cat_printf(
                    annotation, format, j + 1, furi_string_get_cstr(layer_parsed_str));
            } else if(filter == NfcLoggerHistoryLayerFilterTopProtocolSimplified) {
                protocol_formatter->format_history_simplified(
                    request, &item->data, layer_parsed_str);
                furi_string_printf(annotation, "%s", furi_string_get_cstr(layer_parsed_str));
            }
        }
    }

    furi_string_free(layer_parsed_str);
}
