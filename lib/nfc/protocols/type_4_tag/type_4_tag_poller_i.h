#pragma once

#include "type_4_tag_poller.h"

#include <lib/nfc/protocols/iso14443_4a/iso14443_4a_poller_i.h>

#ifdef __cplusplus
extern "C" {
#endif

typedef enum {
    Type4TagPollerStateIdle,
    Type4TagPollerStateSelectApplication,
    Type4TagPollerStateReadCapabilityContainer,
    Type4TagPollerStateReadNdefMessage,
    Type4TagPollerStateReadFailed,
    Type4TagPollerStateReadSuccess,

    Type4TagPollerStateNum,
} Type4TagPollerState;

struct Type4TagPoller {
    Iso14443_4aPoller* iso14443_4a_poller;
    Type4TagPollerState state;
    Type4TagError error;
    Type4TagData* data;
    BitBuffer* tx_buffer;
    BitBuffer* rx_buffer;
    Type4TagPollerEventData type_4_tag_event_data;
    Type4TagPollerEvent type_4_tag_event;
    NfcGenericEvent general_event;
    NfcGenericCallback callback;
    void* context;
};

Type4TagError type_4_tag_process_error(Iso14443_4aError error);

const Type4TagData* type_4_tag_poller_get_data(Type4TagPoller* instance);

Type4TagError type_4_tag_poller_select_app(Type4TagPoller* instance);

Type4TagError type_4_tag_poller_read_cc(Type4TagPoller* instance);

Type4TagError type_4_tag_poller_read_ndef(Type4TagPoller* instance);

#ifdef __cplusplus
}
#endif
