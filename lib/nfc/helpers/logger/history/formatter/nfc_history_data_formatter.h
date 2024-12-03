#pragma once

#include <furi.h>
#include <nfc.h>

#ifdef __cplusplus
extern "C" {
#endif

void nfc_history_data_format(
    NfcProtocol protocol,
    NfcMode mode,
    const NfcHistoryData* data,
    FuriString* output);

#ifdef __cplusplus
}
#endif
