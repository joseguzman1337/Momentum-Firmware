
#include "mf_ultralight_data_formatter.h"
#include "../iso14443_3a/iso14443_3a_listener_data_formatter_i.h"
#include <nfc/protocols/mf_ultralight/mf_ultralight_listener_i.h>
/* 
static const char* events[] = {
    [MfUltralightListenerEventTypeAuth] = "Auth",
}; */

static const char* mfu_cmd[] = {
    [MfUltralightCommandNotFound] = "NotFound",
    [MfUltralightCommandProcessed] = "Processed",
    [MfUltralightCommandProcessedACK] = "Processed ACK",
    [MfUltralightCommandProcessedSilent] = "Processed Silent",
    [MfUltralightCommandNotProcessedNAK] = "Not Processed NAK",
    [MfUltralightCommandNotProcessedSilent] = "Not Processed Silent",
    [MfUltralightCommandNotProcessedAuthNAK] = "Not Processed Auth NAK",
};
/*
static const char* states[] = {
    [Iso14443_3aListenerStateActive] = "Active",
    [Iso14443_3aListenerStateIdle] = "Idle",
};*/

static const char* commands[] = {
    [NfcCommandContinue] = "Continue",
    [NfcCommandReset] = "Reset",
    [NfcCommandSleep] = "Sleep",
    [NfcCommandStop] = "Stop",
};

void mf_ultralight_listener_data_format(const NfcHistoryData* data, FuriString* output) {
    const MfUltralightListenerHistoryData* mf_ultralight_data = data;

    FURI_LOG_D(
        "MFU",
        "E_%02X, MFU_%02X, C_%02X",
        mf_ultralight_data->event,
        mf_ultralight_data->mfu_command,
        mf_ultralight_data->command);

    UNUSED(output);

    const char* event_text =
        iso14443_3a_listener_data_format_event_type(mf_ultralight_data->event);
    //const char* state_text = states[iso14443_3a_data->state];
    const char* process_text = mfu_cmd[mf_ultralight_data->mfu_command];
    const char* result_text = commands[mf_ultralight_data->command];
    furi_string_printf(output, "E=%s, MFU: %s, R=%s", event_text, process_text, result_text);
}

const NfcHistoryItemDataHandler mf_ultralight_listener_data_formatter = {
    .data_size = sizeof(MfUltralightListenerHistoryData),
    .format = mf_ultralight_listener_data_format,
};
