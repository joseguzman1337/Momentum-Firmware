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

static NfcHistoryCrcStatus nfc_history_find_crc_from_chain(const NfcHistoryChain* chain) {
    NfcHistoryCrcStatus status = NfcHistoryCrcNotSet;
    for(size_t i = 0; i < chain->length; i++) {
        for(size_t j = 0; j < COUNT_OF(nfc_history_crc_checker); j++) {
            if(chain->items[i].protocol != nfc_history_crc_checker[j].protocol) continue;
            status = nfc_history_crc_checker[j].checker(&chain->items[i]);
            return status;
        }
    }
    return status;
}

static NfcHistoryCrcStatus nfc_history_find_crc_status(const NfcHistory* history) {
    NfcHistoryCrcStatus status = NfcHistoryCrcNotSet;
    for(size_t i = 0; i < history->base.chain_count; i++) {
        status = nfc_history_find_crc_from_chain(&history->chains[i]);
        if(status != NfcHistoryCrcNotSet) break;
    }
    return status;
}

void nfc_histroy_format_crc_status(const NfcHistory* history, FuriString* crc_status_str) {
    furi_assert(history);
    furi_assert(crc_status_str);
    NfcHistoryCrcStatus status = nfc_history_find_crc_status(history);
    furi_string_printf(crc_status_str, nfc_history_crc_status_message[status]);
}

NfcHistory* nfc_history_alloc(uint8_t max_chain_length) {
    size_t chain_size = sizeof(NfcHistoryItem) * max_chain_length + sizeof(uint8_t);
    NfcHistory* history = malloc(sizeof(NfcHistoryBase) + chain_size * 5);

    ///TODO: maybe make this an input parameter which will be populated from logger instance
    history->base.history_max_size = 5;

    history->base.chain_max_length = max_chain_length;
    return history;
}

void nfc_history_free(NfcHistory* instance) {
    furi_assert(instance);

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

static inline bool nfc_history_chain_load(Stream* stream, NfcHistoryChain* chain) {
    bool result = false;
    do {
        size_t bytes_to_read = sizeof(chain->length);
        size_t read = stream_read(stream, &chain->length, bytes_to_read);
        if(bytes_to_read != read) break;

        bytes_to_read = sizeof(NfcHistoryItem) * chain->length;
        read = stream_read(stream, (uint8_t*)chain->items, bytes_to_read);
        if(bytes_to_read != read) break;

        result = true;
    } while(false);
    return result;
}

bool nfc_history_load(Stream* stream, NfcHistory** instance_ptr) {
    furi_assert(stream);
    furi_assert(instance_ptr);
    bool result = false;
    do {
        NfcHistoryBase base;
        size_t read = stream_read(stream, (uint8_t*)&base, sizeof(NfcHistoryBase));
        if(read != sizeof(NfcHistoryBase)) {
            FURI_LOG_W(TAG, "Unable to read history from file");
            break;
        }
        NfcHistory* history = nfc_history_alloc(base.chain_max_length);
        history->base = base;

        result = true;
        for(size_t i = 0; i < history->base.chain_count; i++) {
            result = nfc_history_chain_load(stream, &history->chains[i]);
            if(!result) {
                FURI_LOG_W(TAG, "Unable to read chain from file");
                break;
            }
        }

        if(result) {
            *instance_ptr = history;
        } else {
            nfc_history_free(history);
        }
    } while(false);
    return result;
}

void nfc_histroy_format_annotation(
    const NfcHistory* instance,
    const FuriHalNfcEvent nfc_event,
    const NfcLoggerHistoryLayerFilter filter,
    FuriString* annotation) {
    furi_assert(instance);
    furi_assert(annotation);

    furi_assert(instance);
    furi_assert(annotation);

    if(nfc_event == 0) return;

    FuriString* layer_parsed_str = furi_string_alloc();
    if(filter == NfcLoggerHistoryLayerFilterAll) {
        nfc_logger_flag_parse(NfcProtocolInvalid, nfc_event, layer_parsed_str);
        furi_string_printf(annotation, "L0(%s)", furi_string_get_cstr(layer_parsed_str));
    }

    for(size_t i = 0; i < instance->base.chain_count; i++) {
        for(size_t j = 0; j < instance->chains[i].length; j++) {
            furi_string_reset(layer_parsed_str);
            const NfcHistoryItem* item = &(instance->chains[i].items[j]);
            if(item->request_flags == 0) continue;

            if(filter == NfcLoggerHistoryLayerFilterTopProtocolOnly &&
               item->protocol != NfcProtocolMfUltralight)
                continue;

            nfc_logger_flag_parse(item->protocol, item->request_flags, layer_parsed_str);

            const char* format =
                (filter == NfcLoggerHistoryLayerFilterTopProtocolOnly) ? "L%d(%s)" : "->L%d(%s)";

            furi_string_cat_printf(
                annotation, format, j + 1, furi_string_get_cstr(layer_parsed_str));
        }
    }

    furi_string_free(layer_parsed_str);
}
