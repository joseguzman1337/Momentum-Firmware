#include "nfc_hal_formatter.h"

//static const char* common_names[] = {};

static const char* events[] = {
    [NfcEventTypeUserAbort] = "Abort",
    [NfcEventTypeFieldOn] = "Field On",
    [NfcEventTypeFieldOff] = "Field Off",
    [NfcEventTypeTxStart] = "TxStart",
    [NfcEventTypeTxEnd] = "TxEnd",
    [NfcEventTypeRxStart] = "RxStart",
    [NfcEventTypeRxEnd] = "RxEnd",

    [NfcEventTypeListenerActivated] = "LstActived",
    [NfcEventTypePollerReady] = "PollerReady",
};

///TODO: Replace numbers with bit defines which will be placed in furi_hal_nfc.h
static const char* hal_nfc_events[] = {
    [0] = "OscOn",
    [1] = "Field On",
    [2] = "Field Off",
    [3] = "Active",
    [4] = "TxStart",
    [5] = "TxEnd",
    [6] = "RxStart",
    [7] = "RxEnd",
    [8] = "Collision",
    [9] = "FwtExpired",
    [10] = "BlockTxExpired",
    [11] = "Timeout",
    [12] = "Abort",
};

const char* nfc_hal_data_format_event_type(const NfcEventType event) {
    return events[event];
}

void nfc_hal_data_format_hal_event_type(const FuriHalNfcEvent event, FuriString* output) {
    uint8_t flags_cnt = 0;
    for(size_t i = 0; i < COUNT_OF(hal_nfc_events); i++) {
        uint32_t flag_mask = (1 << i);
        if(event & flag_mask) {
            furi_string_cat_printf(output, (flags_cnt > 0) ? ", %s" : "%s", hal_nfc_events[i]);
            flags_cnt++;
        }
    }
}
