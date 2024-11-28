#pragma once

#include "nfc_logger_history.h"
#include <furi_hal_nfc.h>
#include <storage/storage.h>
#include <stream/file_stream.h>

#ifdef __cplusplus
extern "C" {
#endif

typedef struct {
    uint8_t length;
    NfcHistoryItem items[];
} FURI_PACKED NfcHistoryChain;

typedef struct {
    uint8_t chain_count;
    uint8_t history_max_size;
    uint8_t chain_max_length;
} NfcHistoryBase;

struct FURI_PACKED NfcHistory {
    NfcHistoryBase base;
    NfcHistoryChain chains[];
    //NfcHistoryChain** chains;
};

NfcHistory* nfc_history_alloc(uint8_t max_chain_cnt);
void nfc_history_free(NfcHistory* instance);

void nfc_history_append(NfcHistory* instance, const NfcHistoryItem* item);

bool nfc_history_load(Stream* stream, NfcHistory** instance_ptr);
void nfc_history_save(File* file, const NfcHistory* instance);

void nfc_histroy_format_crc_status(const NfcHistory* instance, FuriString* crc_status_str);
void nfc_histroy_format_annotation(
    const NfcHistory* instance,
    const FuriHalNfcEvent nfc_event,
    const NfcLoggerHistoryLayerFilter filter,
    FuriString* annotation);

#ifdef __cplusplus
}
#endif
