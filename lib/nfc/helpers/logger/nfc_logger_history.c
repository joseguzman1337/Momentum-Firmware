#include "nfc_logger_history.h"
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

typedef NfcHistoryCrcStatus (*NfcLoggerHistoryCrcChecker)(const NfcLoggerHistory* history);

typedef struct {
    NfcProtocol protocol;
    NfcLoggerHistoryCrcChecker checker;
} NfcLoggerHistoryCrcCheckerItem;

static NfcHistoryCrcStatus nfc_history_crc_checker_dummy(const NfcLoggerHistory* history) {
    UNUSED(history);
    furi_crash("CRC checker not implemented");
    return NfcHistoryCrcInvalidFlags;
}

static NfcHistoryCrcStatus nfc_history_crc_checker_iso14443_3a(const NfcLoggerHistory* history) {
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
    NfcLoggerHistory* history,
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
    NfcLoggerHistory* history,
    size_t history_cnt,
    FuriString* crc_status_str) {
    size_t checker_index = 0;

    if(nfc_history_find_crc_protocol_index(history, history_cnt, &checker_index)) {
        NfcHistoryCrcStatus crc_status =
            nfc_history_crc_checker[checker_index].checker(&history[checker_index]);
        furi_string_printf(crc_status_str, nfc_history_crc_status_message[crc_status]);
    }
}
/* 
void nfc_histroy_format_annotation(
    NfcLoggerHistory* history,
    size_t history_cnt,
    FuriString* annotation) {
    furi_assert(history);
    furi_assert(annotation);
} */
