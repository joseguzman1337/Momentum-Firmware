#pragma once

#include "nfc_logger_history.h"
#include <storage/storage.h>

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

//NfcHistoryChain* nfc_history_chain_alloc(uint8_t item_count_max);
//void nfc_history_chain_free(NfcHistoryChain* chain);

void nfc_history_append(NfcHistory* instance, const NfcHistoryItem* item);

void nfc_history_save(File* file, const NfcHistory* instance);

void nfc_histroy_format_crc_status(
    NfcHistoryItem* history,
    size_t history_cnt,
    FuriString* crc_status_str);

#ifdef __cplusplus
}
#endif
