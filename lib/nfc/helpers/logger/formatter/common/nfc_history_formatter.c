#include "nfc_history_formatter.h"
#include "nfc/helpers/logger/history/nfc_history_i.h"
#include "nfc/helpers/logger/formatter/protocols/_nfc_hal/nfc_hal_formatter.h"
#include "nfc/helpers/logger/formatter/protocols/nfc_protocol_formatters.h"

void nfc_histroy_format_annotation(
    const NfcFormatter* instance,
    const NfcPacket* request,
    const NfcHistory* history,
    const FuriHalNfcEvent nfc_event,
    FuriString* annotation) {
    furi_assert(instance);
    furi_assert(annotation);
    furi_assert(history);
    furi_assert(request);

    FuriString* layer_parsed_str = furi_string_alloc();
    //  if(filter == NfcLoggerHistoryLayerFilterAll) {
    nfc_hal_data_format_hal_event_type(nfc_event, layer_parsed_str);
    furi_string_printf(annotation, "L0(%s)", furi_string_get_cstr(layer_parsed_str));
    //  }

    for(size_t i = 0; i < history->base.chain_count; i++) {
        for(size_t j = 0; j < history->chains[i].length; j++) {
            furi_string_reset(layer_parsed_str);
            const NfcHistoryItemInternal* item =
                (NfcHistoryItemInternal*)&(history->chains[i].items[j]);
            //if(item->base.request_flags == 0) continue;

            ///TODO: Here must be some top protocol varaible, but from where?
            /* if(filter == NfcLoggerHistoryLayerFilterTopProtocolOnly &&
               item->protocol != NfcProtocolMfUltralight)
                continue; */

            //nfc_logger_flag_parse(item->base.protocol, item->base.request_flags, layer_parsed_str);

            const NfcProtocolFormatterBase* protocol_formatter =
                nfc_protocol_formatter_get(item->base.protocol, instance->mode);

            protocol_formatter->format_history(request, item->data, layer_parsed_str);
            /* nfc_history_data_format(
                item->base.protocol, NfcModeListener, item->data, layer_parsed_str); */

            /*      const char* format =
                (filter == NfcLoggerHistoryLayerFilterTopProtocolOnly) ? "L%d(%s)" : "->L%d(%s)"; */

            const char* format = "->L%d(%s)";
            furi_string_cat_printf(
                annotation, format, j + 1, furi_string_get_cstr(layer_parsed_str));
        }
    }

    furi_string_free(layer_parsed_str);
}
