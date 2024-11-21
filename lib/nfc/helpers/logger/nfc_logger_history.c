#include "nfc_logger_history_i.h"
#include <nfc_device.h>

#define TAG "NfcHistory"

typedef enum {
    NfcHistoryCrcNotSet,
    NfcHistoryCrcOk,
    NfcHistoryCrcBad,
    NfcHistoryCrcInvalidFlags,
    NfcHistoryCrcInvalidNum,
} NfcHistoryCrcStatus;

static const char* nfc_history_crc_status_message[NfcHistoryCrcInvalidNum] = {
    [NfcHistoryCrcNotSet] = "",
    [NfcHistoryCrcOk] = "OK",
    [NfcHistoryCrcBad] = "KO",
    [NfcHistoryCrcInvalidFlags] = "ERR",
};

typedef NfcHistoryCrcStatus (*NfcLoggerHistoryCrcChecker)(const NfcHistoryItem* history);

typedef struct {
    NfcProtocol protocol;
    NfcLoggerHistoryCrcChecker checker;
} NfcLoggerHistoryCrcCheckerItem;

static NfcHistoryCrcStatus nfc_history_crc_checker_dummy(const NfcHistoryItem* history) {
    UNUSED(history);
    furi_crash("CRC checker not implemented");
    return NfcHistoryCrcInvalidFlags;
}

static NfcHistoryCrcStatus nfc_history_crc_checker_iso14443_3a(const NfcHistoryItem* history) {
    NfcHistoryCrcStatus crc_status = NfcHistoryCrcNotSet;
    bool crc_ok = NFC_LOG_FLAG_GET(history->request_flags, NFC_FLAG_ISO14443_3A_CRC_OK);
    bool crc_bad = NFC_LOG_FLAG_GET(history->request_flags, NFC_FLAG_ISO14443_3A_CRC_BAD);
    if(crc_ok && !crc_bad)
        crc_status = NfcHistoryCrcOk;
    else if(!crc_ok && crc_bad)
        crc_status = NfcHistoryCrcBad;
    else if(crc_ok && crc_bad) {
        crc_status = NfcHistoryCrcInvalidFlags;
        FURI_LOG_E(TAG, "CRC_OK and CRC_BAD cannot be set both");
    }
    return crc_status;
}

static const NfcLoggerHistoryCrcCheckerItem nfc_history_crc_checker[] = {
    {.protocol = NfcProtocolIso14443_3a, .checker = nfc_history_crc_checker_iso14443_3a},
    {.protocol = NfcProtocolFelica, .checker = nfc_history_crc_checker_dummy},
    {.protocol = NfcProtocolIso15693_3, .checker = nfc_history_crc_checker_dummy},
};

static bool nfc_history_find_crc_protocol_index(
    NfcHistoryItem* history,
    size_t history_cnt,
    size_t* checker_index) {
    bool found = false;

    for(size_t i = 0; i < history_cnt; i++) {
        for(size_t j = 0; j < COUNT_OF(nfc_history_crc_checker); j++) {
            if(nfc_history_crc_checker[j].protocol != history[i].protocol) continue;
            const char* protocol_name = nfc_device_get_protocol_name(history[i].protocol);
            FURI_LOG_D(TAG, "Found CRC checker: %s", protocol_name);
            found = true;
            *checker_index = j;
            break;
        }
    }
    return found;
}

void nfc_histroy_format_crc_status(
    NfcHistoryItem* history,
    size_t history_cnt,
    FuriString* crc_status_str) {
    size_t checker_index = 0;

    if(nfc_history_find_crc_protocol_index(history, history_cnt, &checker_index)) {
        NfcHistoryCrcStatus crc_status =
            nfc_history_crc_checker[checker_index].checker(&history[checker_index]);
        furi_string_printf(crc_status_str, nfc_history_crc_status_message[crc_status]);
    }
}

///TODO: make inline
/* static inline NfcHistoryChain* nfc_history_chain_alloc(uint8_t item_count_max) {
    furi_assert(item_count_max > 0);
    NfcHistoryChain* chain = malloc(sizeof(NfcHistoryChain));
    chain->items = malloc(sizeof(NfcHistoryItem*) * item_count_max);

    return chain;
}

///TODO: make inline
static inline void nfc_history_chain_free(NfcHistoryChain* chain) {
    furi_assert(chain);
    free(chain->items);
    free(chain);
} */

NfcHistory* nfc_history_alloc(uint8_t max_chain_length) {
    //NfcHistory* history = malloc(sizeof(NfcHistory));
    size_t chain_size = sizeof(NfcHistoryItem) * max_chain_length + sizeof(uint8_t);
    NfcHistory* history = malloc(sizeof(NfcHistoryBase) + chain_size * 5);

    ///TODO: maybe make this an input parameter which will be populated from logger instance
    history->base.history_max_size = 5;

    history->base.chain_max_length = max_chain_length;

    //history->chains = malloc(sizeof(NfcHistoryChain*) * history->base.history_max_size);
    /*    for(size_t i = 0; i < history->base.history_max_size; i++) {
        history->chains[i] = nfc_history_chain_alloc(history->base.chain_max_length);
    } */

    //history->chains[0] = nfc_history_chain_alloc(history->base.chain_max_length);
    return history;
}

void nfc_history_free(NfcHistory* instance) {
    furi_assert(instance);

    /*  NfcHistoryBase* base = &instance->base;
    for(size_t i = 0; i < base->chain_count; i++) {
        nfc_history_chain_free(instance->chains[i]);
    }
    free(instance->chains); */
    free(instance);
}

void nfc_history_append(NfcHistory* instance, const NfcHistoryItem* item) {
    furi_assert(instance);
    furi_assert(item);
    NfcHistoryBase* base = &instance->base;
    do {
        if(base->chain_count == base->history_max_size) {
            FURI_LOG_W(TAG, "History is full");
            break;
        }

        if(base->chain_count == 0) base->chain_count += 1;

        uint8_t current_chain_index = base->chain_count - 1;
        ///TODO: split this into some static inline functions
        if(instance->chains[current_chain_index].length == base->chain_max_length) {
            base->chain_count += 1;
            current_chain_index += 1;
            // instance->chains[base->chain_count] = nfc_history_chain_alloc(base->chain_max_length);
        }

        NfcHistoryChain* chain = &instance->chains[current_chain_index];
        chain->items[chain->length] = *item;
        chain->length++;
    } while(false);
}

static inline void nfc_history_chain_save(File* file, const NfcHistoryChain* chain) {
    storage_file_write(file, &chain->length, sizeof(chain->length));
    storage_file_write(file, chain->items, sizeof(NfcHistoryItem) * chain->length);
}

void nfc_history_save(File* file, const NfcHistory* instance) {
    furi_assert(file);
    furi_assert(instance);
    storage_file_write(file, &instance->base, sizeof(NfcHistoryBase));
    for(uint8_t i = 0; i < instance->base.chain_count; i++) {
        nfc_history_chain_save(file, &instance->chains[i]);
    }
}

/* 
void nfc_histroy_format_annotation(
    NfcHistoryItem* history,
    size_t history_cnt,
    FuriString* annotation) {
    furi_assert(history);
    furi_assert(annotation);
} */
