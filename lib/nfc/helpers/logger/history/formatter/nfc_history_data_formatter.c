
#include "nfc_history_data_formatter.h"
#include "nfc_history_data_formatter_base.h"

#include "protocols/iso14443_3a/iso14443_3a_listener_data_formatter.h"
#include "protocols/mf_ultralight/mf_ultralight_data_formatter.h"

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
