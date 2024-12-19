#include "nfc_protocol_formatters.h"
#include "iso14443_3a_listener_data_formatter.h"
#include "mf_ultralight_listener_data_formatter.h"
#include "felica_listener_data_formatter.h"

#include "iso14443_3a_poller_data_formatter.h"
#include "iso15693_3_poller_data_formatter.h"
#include "mf_ultralight_poller_data_formatter.h"
#include "felica_poller_data_formatter.h"

#define TAG "NfcProtocolFormatter"

static const NfcProtocolFormatterBase* listener_formatters[NfcProtocolNum] = {
    [NfcProtocolIso14443_3a] = &iso14443_3a_listener_data_formatter,
    [NfcProtocolIso14443_3b] = NULL,
    [NfcProtocolIso14443_4a] = NULL,
    [NfcProtocolIso14443_4b] = NULL,
    [NfcProtocolIso15693_3] = NULL,
    [NfcProtocolFelica] = &felica_listener_data_formatter,
    [NfcProtocolMfUltralight] = &mf_ultralight_listener_data_formatter,
    [NfcProtocolMfClassic] = NULL,
    [NfcProtocolMfPlus] = NULL,
    [NfcProtocolMfDesfire] = NULL,
    [NfcProtocolSlix] = NULL,
    [NfcProtocolSt25tb] = NULL,
};

static const NfcProtocolFormatterBase* poller_formatters[NfcProtocolNum] = {
    [NfcProtocolIso14443_3a] = &iso14443_3a_poller_data_formatter,
    [NfcProtocolIso14443_3b] = NULL,
    [NfcProtocolIso14443_4a] = NULL,
    [NfcProtocolIso14443_4b] = NULL,
    [NfcProtocolIso15693_3] = &iso15693_3_poller_data_formatter,
    [NfcProtocolFelica] = &felica_poller_data_formatter,
    [NfcProtocolMfUltralight] = &mf_ultralight_poller_data_formatter,
    [NfcProtocolMfClassic] = NULL,
    [NfcProtocolMfPlus] = NULL,
    [NfcProtocolMfDesfire] = NULL,
    [NfcProtocolSlix] = NULL,
    [NfcProtocolSt25tb] = NULL,
};

const NfcProtocolFormatterBase* nfc_protocol_formatter_get(NfcProtocol protocol, NfcMode mode) {
    furi_assert(protocol < NfcProtocolNum);
    furi_assert(mode < NfcModeNum);

    const NfcProtocolFormatterBase** formatters = (mode == NfcModeListener) ? listener_formatters :
                                                                              poller_formatters;

    const NfcProtocolFormatterBase* formatter = formatters[protocol];
    if(!formatter) {
        FURI_LOG_W(TAG, "Formatter for protocol: %d not found", protocol);
    }
    return formatter;
}
