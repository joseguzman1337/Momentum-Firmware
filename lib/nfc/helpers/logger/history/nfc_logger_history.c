#include "nfc_logger_history_i.h"

#include <nfc/protocols/iso14443_3a/iso14443_3a_listener_i.h>
#include <nfc/protocols/mf_ultralight/mf_ultralight_listener_i.h>

#include <nfc/protocols/iso14443_3a/iso14443_3a_poller_i.h>
#include <nfc/protocols/mf_ultralight/mf_ultralight_poller_i.h>

//#include "../formatter/nfc_formatter.h"

#include <nfc_device.h>

#define TAG "NfcHistory"

/* typedef enum {
    NfcHistoryCrcNotSet,
    NfcHistoryCrcOk,
    NfcHistoryCrcBad,
    NfcHistoryCrcInvalidFlags,
    NfcHistoryCrcInvalidNum,
} NfcHistoryCrcStatus; */

//typedef NfcHistoryCrcStatus (*NfcLoggerHistoryCrcChecker)(const NfcHistoryItem* history);

/* typedef struct {
    NfcProtocol protocol;
    NfcLoggerHistoryCrcChecker checker;
} NfcLoggerHistoryCrcCheckerItem;

static NfcHistoryCrcStatus nfc_history_crc_checker_dummy(const NfcHistoryItem* history) {
    UNUSED(history);
    furi_crash("CRC checker not implemented");
    return NfcHistoryCrcInvalidFlags;
} */

/* typedef NfcHistory* (*NfcHistoryAllocCallback)(void);
typedef size_t (*NfcHistoryGetDataSizeCallback)(void);

typedef struct {
    NfcHistoryAllocCallback alloc;
    NfcHistoryGetDataSizeCallback get_size;
} NfcHistoryBase; */

/* static NfcHistoryCrcStatus nfc_history_crc_checker_iso14443_3a(const NfcHistoryItem* history) {
    NfcHistoryCrcStatus crc_status = NfcHistoryCrcNotSet;
    bool crc_ok = NFC_LOG_FLAG_GET(history->base.request_flags, NFC_FLAG_ISO14443_3A_CRC_OK);
    bool crc_bad = NFC_LOG_FLAG_GET(history->base.request_flags, NFC_FLAG_ISO14443_3A_CRC_BAD);
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
            if(chain->items[i].base.protocol != nfc_history_crc_checker[j].protocol) continue;
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
} */

static const uint8_t listener_history_chain_size[NfcProtocolNum] = {
    [NfcProtocolIso14443_3a] = sizeof(Iso14443_3aListenerHistoryData),
    [NfcProtocolMfUltralight] = sizeof(MfUltralightListenerHistoryData),
};

static const uint8_t poller_history_chain_size[NfcProtocolNum] = {
    [NfcProtocolIso14443_3a] = sizeof(Iso14443_3aPollerHistoryData),
    [NfcProtocolMfUltralight] = sizeof(MfUltralightPollerHistoryData),
};

static uint8_t nfc_history_get_chain_size_bytes(NfcProtocol protocol, NfcMode mode) {
    const uint8_t* history_data_size_source =
        (mode == NfcModeListener) ? listener_history_chain_size : poller_history_chain_size;

    uint8_t chain_size_bytes = sizeof(uint8_t);
    do {
        chain_size_bytes += sizeof(NfcHistoryItemBase);
        uint8_t buf = history_data_size_source[protocol];

        FURI_LOG_D(
            TAG,
            "Protocol: %d data_size: %d item base: %d",
            protocol,
            buf,
            sizeof(NfcHistoryItemBase));

        chain_size_bytes += buf; /* history_data_size_source[protocol] */

        protocol = nfc_protocol_get_parent(protocol);
    } while(protocol != NfcProtocolInvalid);
    FURI_LOG_D(TAG, "Chain size: %d", chain_size_bytes);
    return chain_size_bytes;
}

uint8_t nfc_history_get_size_bytes(NfcProtocol protocol, NfcMode mode, uint8_t max_chain_count) {
    const uint8_t chain_size_bytes = nfc_history_get_chain_size_bytes(protocol, mode);
    uint8_t history_size_bytes = sizeof(NfcHistoryBase) + chain_size_bytes * max_chain_count;
    FURI_LOG_D(TAG, "History size: %d", history_size_bytes);
    return history_size_bytes;
}

NfcHistory* nfc_history_alloc(uint8_t history_size_bytes, uint8_t max_chain_count) {
    /*     size_t chain_size = sizeof(NfcHistoryItemBase) * max_chain_length + sizeof(uint8_t);
    NfcHistory* history = malloc(sizeof(NfcHistoryBase) + chain_size * 5);

    ///TODO: maybe make this an input parameter which will be populated from logger instance
    history->base.history_max_size = 5;

    history->base.chain_max_length = max_chain_length; */
    NfcHistory* history = malloc(history_size_bytes);
    history->base.history_size_bytes = history_size_bytes;
    history->base.max_chain_count = max_chain_count;
    //history->base.
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
        if(base->chain_count == base->max_chain_count) {
            FURI_LOG_W(TAG, "History is full");
            break;
        }

        if(base->chain_count == 0) base->chain_count += 1;

        uint8_t current_chain_index = base->chain_count - 1;
        ///TODO: split this into some static inline functions
        if(instance->chains[current_chain_index].length == base->max_chain_count) {
            base->chain_count += 1;
            current_chain_index += 1;
            // instance->chains[base->chain_count] = nfc_history_chain_alloc(base->chain_max_length);
        }

        NfcHistoryChain* chain = &instance->chains[current_chain_index];
        NfcHistoryItemInternal* chain_item = (NfcHistoryItemInternal*)&chain->items[chain->length];
        chain_item->base = item->base;
        memcpy(chain_item->data, item->data, item->base.data_block_size);
        //uint8_t* data_ptr = ((uint8_t*)&chain->items[chain->length]) + sizeof(NfcHistoryItemBase);
        //memcpy(data_ptr, item->data, item->base.data_block_size);

        chain->length++;
    } while(false);
}

static inline void nfc_history_chain_save(File* file, const NfcHistoryChain* chain) {
    storage_file_write(file, &chain->length, sizeof(chain->length));
    for(size_t i = 0; i < chain->length; i++) {
        const NfcHistoryItemInternal* item = (NfcHistoryItemInternal*)&chain->items[i];
        storage_file_write(file, &item->base, sizeof(NfcHistoryItemBase));
        //&item->base + sizeof(NfcHistoryItemBase)
        storage_file_write(file, item->data, item->base.data_block_size);
    }

    //storage_file_write(file, chain->items, sizeof(NfcHistoryItem) * chain->length);
}

void nfc_history_save(File* file, const NfcHistory* instance) {
    furi_assert(file);
    furi_assert(instance);
    storage_file_write(file, &instance->base, sizeof(NfcHistoryBase));
    for(uint8_t i = 0; i < instance->base.chain_count; i++) {
        nfc_history_chain_save(file, &instance->chains[i]);
    }
}

static inline bool nfc_history_item_load(Stream* stream, NfcHistoryItemInternal* item) {
    bool result = false;
    do {
        size_t bytes_to_read = sizeof(NfcHistoryItemBase);
        size_t read = stream_read(stream, (uint8_t*)&item->base, bytes_to_read);
        if(bytes_to_read != read) break;

        bytes_to_read = item->base.data_block_size;
        read = stream_read(stream, item->data, bytes_to_read);
        if(bytes_to_read != read) break;

        result = true;
    } while(false);
    return result;
}

static inline bool nfc_history_chain_load(Stream* stream, NfcHistoryChain* chain) {
    bool result = false;
    do {
        size_t bytes_to_read = sizeof(chain->length);
        size_t read = stream_read(stream, &chain->length, bytes_to_read);
        if(bytes_to_read != read) break;

        for(size_t i = 0; i < chain->length; i++) {
            result = nfc_history_item_load(stream, (NfcHistoryItemInternal*)&chain->items[i]);
            if(!result) break;
            /*    bytes_to_read = sizeof(NfcHistoryItemBase);
            NfcHistoryItem* item = &chain->items[i];
            read = stream_read(stream, (uint8_t*)&item->base, bytes_to_read);
            if(bytes_to_read != read) break;

            bytes_to_read = item->base.data_block_size;
            read = stream_read(stream, (uint8_t*)item->data, bytes_to_read);
            if(bytes_to_read != read) break; */
        }

        /*  bytes_to_read = sizeof(NfcHistoryItemBase);
        //bytes_to_read = sizeof(NfcHistoryItem) * chain->length;
        read = stream_read(stream, (uint8_t*)chain->items, bytes_to_read);
        if(bytes_to_read != read) break; */

        //result = true;
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
        NfcHistory* history = nfc_history_alloc(base.history_size_bytes, base.max_chain_count);
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
