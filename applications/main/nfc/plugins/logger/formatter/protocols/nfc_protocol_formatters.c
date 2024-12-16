#include "nfc_protocol_formatters.h"
#include "iso14443_3a/iso14443_3a_listener_data_formatter.h"
#include "mf_ultralight/mf_ultralight_listener_data_formatter.h"
#include "felica/felica_listener_data_formatter.h"

#include "iso14443_3a/iso14443_3a_poller_data_formatter.h"
#include "mf_ultralight/mf_ultralight_poller_data_formatter.h"
#include "felica/felica_poller_data_formatter.h"

static const NfcProtocolFormatterBase* listener_formatters[NfcProtocolNum] = {
    [NfcProtocolIso14443_3a] = &iso14443_3a_listener_data_formatter,
    [NfcProtocolMfUltralight] = &mf_ultralight_listener_data_formatter,
    [NfcProtocolFelica] = &felica_listener_data_formatter,
};

static const NfcProtocolFormatterBase* poller_formatters[] = {
    [NfcProtocolIso14443_3a] = &iso14443_3a_poller_data_formatter,
    [NfcProtocolMfUltralight] = &mf_ultralight_poller_data_formatter,
    [NfcProtocolFelica] = &felica_poller_data_formatter,
};

const NfcProtocolFormatterBase* nfc_protocol_formatter_get(NfcProtocol protocol, NfcMode mode) {
    furi_assert(protocol < NfcProtocolNum);
    furi_assert(mode < NfcModeNum);

    const NfcProtocolFormatterBase** formatters = (mode == NfcModeListener) ? listener_formatters :
                                                                              poller_formatters;
    return formatters[protocol];
}
