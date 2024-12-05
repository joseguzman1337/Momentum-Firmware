#pragma once

#include <furi.h>
#include <furi_hal_nfc.h>

#include "../nfc_formatter_context.h"
#include "nfc/helpers/logger/history/nfc_logger_history.h"
#include "nfc/helpers/logger/nfc_packet_data_type_i.h"

#ifdef __cplusplus
extern "C" {
#endif

void nfc_histroy_format_annotation(
    const NfcFormatter* instance,
    const NfcPacket* request,
    const NfcHistory* history,
    const FuriHalNfcEvent nfc_event,
    FuriString* annotation);

#ifdef __cplusplus
}
#endif
