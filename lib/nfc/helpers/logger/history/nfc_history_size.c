#include "nfc_history_size.h"
#include "nfc_history_i.h"

#include <nfc/protocols/iso14443_3a/iso14443_3a_listener_i.h>
#include <nfc/protocols/mf_ultralight/mf_ultralight_listener_i.h>

#include <nfc/protocols/iso14443_3a/iso14443_3a_poller_i.h>
#include <nfc/protocols/mf_ultralight/mf_ultralight_poller_i.h>

#define TAG "NfcHistorySize"

static const uint8_t listener_history_chain_size[NfcProtocolNum] = {
    [NfcProtocolIso14443_3a] = sizeof(Iso14443_3aListenerHistoryData),
    [NfcProtocolMfUltralight] = sizeof(MfUltralightListenerHistoryData),
};

static const uint8_t poller_history_chain_size[NfcProtocolNum] = {
    [NfcProtocolIso14443_3a] = sizeof(Iso14443_3aPollerHistoryData),
    [NfcProtocolMfUltralight] = sizeof(MfUltralightPollerHistoryData),
};

static uint8_t nfc_history_get_chain_size_bytes(NfcProtocol protocol, NfcMode mode) {
    const uint8_t* history_data_size_source =
        (mode == NfcModeListener) ? listener_history_chain_size : poller_history_chain_size;

    uint8_t chain_size_bytes = sizeof(NfcChainLength);
    do {
        chain_size_bytes += sizeof(NfcHistoryItemBase);
        uint8_t buf = history_data_size_source[protocol];

        FURI_LOG_D(
            TAG,
            "Protocol: %d data_size: %d item base: %d",
            protocol,
            buf,
            sizeof(NfcHistoryItemBase));

        chain_size_bytes += buf;
        protocol = nfc_protocol_get_parent(protocol);
    } while(protocol != NfcProtocolInvalid);
    FURI_LOG_D(TAG, "Chain size: %d", chain_size_bytes);
    return chain_size_bytes;
}

uint8_t nfc_history_get_size_bytes(NfcProtocol protocol, NfcMode mode, uint8_t max_chain_count) {
    const uint8_t chain_size_bytes = nfc_history_get_chain_size_bytes(protocol, mode);
    uint8_t history_size_bytes = sizeof(NfcHistoryBase) + chain_size_bytes * max_chain_count;
    FURI_LOG_D(TAG, "History size: %d", history_size_bytes);
    return history_size_bytes;
}
