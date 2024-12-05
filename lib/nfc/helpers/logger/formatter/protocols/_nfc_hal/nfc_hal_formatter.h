#pragma once
#include <nfc.h>
#include <furi_hal_nfc.h>

#ifdef __cplusplus
extern "C" {
#endif

const char* nfc_hal_data_format_event_type(const NfcEventType event);
void nfc_hal_data_format_hal_event_type(const FuriHalNfcEvent event, FuriString* output);

#ifdef __cplusplus
}
#endif
