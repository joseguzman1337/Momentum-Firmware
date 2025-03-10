#include "type_4_tag_poller_i.h"
#include "type_4_tag_i.h"

#include <nfc/protocols/nfc_poller_base.h>

#include <furi.h>

#define TAG "Type4TagPoller"

// Read returns 2 byte status trailer, write sends 5 byte command header
#define TYPE_4_TAG_BUF_SIZE (TYPE_4_TAG_ISO_RW_CHUNK_LEN + 5)

typedef NfcCommand (*Type4TagPollerReadHandler)(Type4TagPoller* instance);

const Type4TagData* type_4_tag_poller_get_data(Type4TagPoller* instance) {
    furi_assert(instance);

    return instance->data;
}

static Type4TagPoller* type_4_tag_poller_alloc(Iso14443_4aPoller* iso14443_4a_poller) {
    Type4TagPoller* instance = malloc(sizeof(Type4TagPoller));
    instance->iso14443_4a_poller = iso14443_4a_poller;
    instance->data = type_4_tag_alloc();
    instance->tx_buffer = bit_buffer_alloc(TYPE_4_TAG_BUF_SIZE);
    instance->rx_buffer = bit_buffer_alloc(TYPE_4_TAG_BUF_SIZE);

    instance->type_4_tag_event.data = &instance->type_4_tag_event_data;

    instance->general_event.protocol = NfcProtocolType4Tag;
    instance->general_event.event_data = &instance->type_4_tag_event;
    instance->general_event.instance = instance;

    return instance;
}

static void type_4_tag_poller_free(Type4TagPoller* instance) {
    furi_assert(instance);

    type_4_tag_free(instance->data);
    bit_buffer_free(instance->tx_buffer);
    bit_buffer_free(instance->rx_buffer);
    free(instance);
}

static NfcCommand type_4_tag_poller_handler_idle(Type4TagPoller* instance) {
    bit_buffer_reset(instance->tx_buffer);
    bit_buffer_reset(instance->rx_buffer);

    iso14443_4a_copy(
        instance->data->iso14443_4a_data,
        iso14443_4a_poller_get_data(instance->iso14443_4a_poller));

    instance->state = Type4TagPollerStateSelectApplication;
    return NfcCommandContinue;
}

static NfcCommand type_4_tag_poller_handler_select_app(Type4TagPoller* instance) {
    instance->error = type_4_tag_poller_select_app(instance);
    if(instance->error == Type4TagErrorNone) {
        FURI_LOG_D(TAG, "Select application success");
        instance->state = Type4TagPollerStateReadCapabilityContainer;
    } else {
        FURI_LOG_E(TAG, "Failed to select application");
        iso14443_4a_poller_halt(instance->iso14443_4a_poller);
        instance->state = Type4TagPollerStateReadFailed;
    }

    return NfcCommandContinue;
}

static NfcCommand type_4_tag_poller_handler_read_cc(Type4TagPoller* instance) {
    instance->error = type_4_tag_poller_read_cc(instance);
    if(instance->error == Type4TagErrorNone) {
        FURI_LOG_D(TAG, "Read CC success");
        instance->state = Type4TagPollerStateReadNdefMessage;
    } else {
        FURI_LOG_E(TAG, "Failed to read CC");
        iso14443_4a_poller_halt(instance->iso14443_4a_poller);
        instance->state = Type4TagPollerStateReadFailed;
    }

    return NfcCommandContinue;
}

static NfcCommand type_4_tag_poller_handler_read_ndef(Type4TagPoller* instance) {
    instance->error = type_4_tag_poller_read_ndef(instance);
    if(instance->error == Type4TagErrorNone) {
        FURI_LOG_D(TAG, "Read NDEF success");
        instance->state = Type4TagPollerStateReadSuccess;
    } else {
        FURI_LOG_E(TAG, "Failed to read NDEF");
        iso14443_4a_poller_halt(instance->iso14443_4a_poller);
        instance->state = Type4TagPollerStateReadFailed;
    }

    return NfcCommandContinue;
}

static NfcCommand type_4_tag_poller_handler_read_fail(Type4TagPoller* instance) {
    FURI_LOG_D(TAG, "Read Failed");
    iso14443_4a_poller_halt(instance->iso14443_4a_poller);
    instance->type_4_tag_event.type = Type4TagPollerEventTypeReadFailed;
    instance->type_4_tag_event.data->error = instance->error;
    NfcCommand command = instance->callback(instance->general_event, instance->context);
    instance->state = Type4TagPollerStateIdle;
    return command;
}

static NfcCommand type_4_tag_poller_handler_read_success(Type4TagPoller* instance) {
    FURI_LOG_D(TAG, "Read success.");
    iso14443_4a_poller_halt(instance->iso14443_4a_poller);
    instance->type_4_tag_event.type = Type4TagPollerEventTypeReadSuccess;
    NfcCommand command = instance->callback(instance->general_event, instance->context);
    return command;
}

static const Type4TagPollerReadHandler type_4_tag_poller_read_handler[Type4TagPollerStateNum] = {
    [Type4TagPollerStateIdle] = type_4_tag_poller_handler_idle,
    [Type4TagPollerStateSelectApplication] = type_4_tag_poller_handler_select_app,
    [Type4TagPollerStateReadCapabilityContainer] = type_4_tag_poller_handler_read_cc,
    [Type4TagPollerStateReadNdefMessage] = type_4_tag_poller_handler_read_ndef,
    [Type4TagPollerStateReadFailed] = type_4_tag_poller_handler_read_fail,
    [Type4TagPollerStateReadSuccess] = type_4_tag_poller_handler_read_success,
};

static void type_4_tag_poller_set_callback(
    Type4TagPoller* instance,
    NfcGenericCallback callback,
    void* context) {
    furi_assert(instance);
    furi_assert(callback);

    instance->callback = callback;
    instance->context = context;
}

static NfcCommand type_4_tag_poller_run(NfcGenericEvent event, void* context) {
    furi_assert(event.protocol == NfcProtocolIso14443_4a);

    Type4TagPoller* instance = context;
    furi_assert(instance);
    furi_assert(instance->callback);

    const Iso14443_4aPollerEvent* iso14443_4a_event = event.event_data;
    furi_assert(iso14443_4a_event);

    NfcCommand command = NfcCommandContinue;

    if(iso14443_4a_event->type == Iso14443_4aPollerEventTypeReady) {
        command = type_4_tag_poller_read_handler[instance->state](instance);
    } else if(iso14443_4a_event->type == Iso14443_4aPollerEventTypeError) {
        instance->type_4_tag_event.type = Type4TagPollerEventTypeReadFailed;
        instance->type_4_tag_event.data->error =
            type_4_tag_process_error(iso14443_4a_event->data->error);
        command = instance->callback(instance->general_event, instance->context);
    }

    return command;
}

static bool type_4_tag_poller_detect(NfcGenericEvent event, void* context) {
    furi_assert(event.protocol == NfcProtocolIso14443_4a);

    Type4TagPoller* instance = context;
    furi_assert(instance);

    const Iso14443_4aPollerEvent* iso14443_4a_event = event.event_data;
    furi_assert(iso14443_4a_event);

    bool protocol_detected = false;

    if(iso14443_4a_event->type == Iso14443_4aPollerEventTypeReady) {
        Type4TagError error = type_4_tag_poller_select_app(instance);
        if(error == Type4TagErrorNone) {
            protocol_detected = true;
        }
    }

    return protocol_detected;
}

const NfcPollerBase type_4_tag_poller = {
    .alloc = (NfcPollerAlloc)type_4_tag_poller_alloc,
    .free = (NfcPollerFree)type_4_tag_poller_free,
    .set_callback = (NfcPollerSetCallback)type_4_tag_poller_set_callback,
    .run = (NfcPollerRun)type_4_tag_poller_run,
    .detect = (NfcPollerDetect)type_4_tag_poller_detect,
    .get_data = (NfcPollerGetData)type_4_tag_poller_get_data,
};
