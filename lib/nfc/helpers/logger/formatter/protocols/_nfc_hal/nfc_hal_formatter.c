#include "nfc_hal_formatter.h"

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

const char* nfc_hal_data_format_event_type(const NfcEventType event) {
    return events[event];
}
