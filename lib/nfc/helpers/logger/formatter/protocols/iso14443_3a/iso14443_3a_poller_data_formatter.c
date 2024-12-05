#include "iso14443_3a_poller_data_formatter_i.h"
#include "../_nfc_hal/nfc_hal_formatter.h"

static const char* states[] = {
    [Iso14443_3aPollerStateIdle] = "Idle",
    [Iso14443_3aPollerStateColResInProgress] = "Collision Resolve",
    [Iso14443_3aPollerStateColResFailed] = "Collision Resolve Failed",
    [Iso14443_3aPollerStateActivated] = "Activated",
};

static const char* commands[] = {
    [NfcCommandContinue] = "Continue",
    [NfcCommandReset] = "Reset",
    [NfcCommandSleep] = "Sleep",
    [NfcCommandStop] = "Stop",
};

static const char* poller_events[] = {
    [Iso14443_3aPollerEventTypeError] = "Error",
    [Iso14443_3aPollerEventTypeReady] = "Ready",
};

const char* iso14443_3a_poller_data_format_event_type(const Iso14443_3aPollerEventType event) {
    return poller_events[event];
}

static void iso14443_3a_poller_data_format(
    const NfcPacket* response,
    const NfcHistoryData* data,
    FuriString* output) {
    UNUSED(response);
    const Iso14443_3aPollerHistoryData* poller_data = data;

    const char* event_text = nfc_hal_data_format_event_type(poller_data->event);
    const char* state_text = states[poller_data->state];
    const char* command_text = commands[poller_data->command];
    furi_string_printf(output, "E=%s, S=%s, C=%s", event_text, state_text, command_text);
}

static NfcHistoryCrcStatus iso14443_3a_poller_get_crc_status(const NfcHistoryData* data) {
    const Iso14443_3aPollerHistoryData* poller_data = data;
    return (poller_data->error == Iso14443_3aErrorWrongCrc) ? NfcHistoryCrcBad : NfcHistoryCrcOk;
}

const NfcProtocolFormatterBase iso14443_3a_poller_data_formatter = {
    .format_history = iso14443_3a_poller_data_format,
    .get_crc_status = iso14443_3a_poller_get_crc_status,
};
