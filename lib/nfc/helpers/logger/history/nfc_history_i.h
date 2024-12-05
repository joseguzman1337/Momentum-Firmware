#pragma once

#include "nfc_history.h"
#include <furi_hal_nfc.h>
#include <storage/storage.h>
#include <stream/file_stream.h>

#include "nfc_history_chain_data_type_i.h"

#ifdef __cplusplus
extern "C" {
#endif

//uint8_t nfc_history_get_size_bytes(NfcProtocol protocol, NfcMode mode, uint8_t max_chain_count);
NfcHistory* nfc_history_alloc(uint8_t history_size_bytes, uint8_t max_chain_count);
void nfc_history_free(NfcHistory* instance);

void nfc_history_append(NfcHistory* instance, const NfcHistoryItem* item);

bool nfc_history_load(Stream* stream, NfcHistory** instance_ptr);
void nfc_history_save(File* file, const NfcHistory* instance);

#ifdef __cplusplus
}
#endif
