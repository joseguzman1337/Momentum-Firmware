
#include "mf_ultralight_listener_data_formatter.h"
#include "../iso14443_3a/iso14443_3a_listener_data_formatter_i.h"
//#include "../../common/nfc_transaction_formatter.h"
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

static const char* commands[] = {
    [NfcCommandContinue] = "Continue",
    [NfcCommandReset] = "Reset",
    [NfcCommandSleep] = "Sleep",
    [NfcCommandStop] = "Stop",
};

static void mf_ultralight_listener_data_format(
    const NfcPacket* request,
    const NfcHistoryData* data,
    FuriString* output) {
    const MfUltralightListenerHistoryData* mf_ultralight_data = data;
    UNUSED(request);
    FURI_LOG_D(
        "MFU",
        "E_%02X, MFU_%02X, C_%02X",
        mf_ultralight_data->event,
        mf_ultralight_data->mfu_command,
        mf_ultralight_data->command);

    UNUSED(output);

    const char* event_text =
        iso14443_3a_listener_data_format_event_type(mf_ultralight_data->event);
    const char* process_text = mfu_cmd[mf_ultralight_data->mfu_command];
    const char* result_text = commands[mf_ultralight_data->command];
    furi_string_printf(output, "E=%s, MFU: %s, R=%s", event_text, process_text, result_text);
}

static NfcHistoryCrcStatus mf_ultralight_listener_get_crc_status(const NfcHistoryData* data) {
    const MfUltralightListenerHistoryData* mf_ultralight_data = data;
    NfcHistoryCrcStatus status = NfcHistoryCrcNotSet;
    if(mf_ultralight_data->event == Iso14443_3aListenerEventTypeReceivedStandardFrame)
        status = NfcHistoryCrcOk;
    else if(mf_ultralight_data->event == Iso14443_3aListenerEventTypeReceivedData)
        status = NfcHistoryCrcBad;
    return status;
}

const NfcProtocolFormatterBase mf_ultralight_listener_data_formatter = {
    .format_history = mf_ultralight_listener_data_format,
    .get_crc_status = mf_ultralight_listener_get_crc_status,
};
