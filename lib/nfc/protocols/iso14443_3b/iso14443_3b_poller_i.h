#pragma once

#include "iso14443_3b_poller.h"
#include "iso14443_3b_i.h"
#include <helpers/logger/nfc_logger_i.h>

#ifdef __cplusplus
extern "C" {
#endif

#define ISO14443_3B_POLLER_MAX_BUFFER_SIZE (256U)

typedef enum {
    Iso14443_3bPollerStateIdle,
    Iso14443_3bPollerStateColResInProgress,
    Iso14443_3bPollerStateColResFailed,
    Iso14443_3bPollerStateActivationInProgress,
    Iso14443_3bPollerStateActivationFailed,
    Iso14443_3bPollerStateActivated,
} Iso14443_3bPollerState;

typedef struct {
    NfcEventType event;
    Iso14443_3bPollerState state;
    Iso14443_3bError error;
    NfcCommand command;
} FURI_PACKED Iso14443_3bPollerHistoryData;

struct Iso14443_3bPoller {
    Nfc* nfc;
    Iso14443_3bPollerState state;
    Iso14443_3bData* data;
    BitBuffer* tx_buffer;
    BitBuffer* rx_buffer;

    NfcGenericEvent general_event;
    Iso14443_3bPollerEvent iso14443_3b_event;
    Iso14443_3bPollerEventData iso14443_3b_event_data;
    NfcGenericCallback callback;
    NfcGenericLogHistoryCallback log_callback;
    NfcHistoryItem history;
    Iso14443_3bPollerHistoryData history_data;
    void* context;
};

const Iso14443_3bData* iso14443_3b_poller_get_data(Iso14443_3bPoller* instance);

#ifdef __cplusplus
}
#endif
