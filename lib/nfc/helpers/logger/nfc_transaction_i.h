#pragma once

#include "nfc_transaction.h"
#include "history/nfc_logger_history_i.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef struct {
    uint32_t time;
    uint32_t flags;
    size_t data_size;
    uint8_t* data;
} NfcPacket;

typedef struct {
    uint32_t id;
    NfcTransactionType type;
    FuriHalNfcEvent nfc_event;
    uint32_t time; ///TODO: optional
} FURI_PACKED NfcTransactionHeader;

struct FURI_PACKED NfcTransaction {
    NfcTransactionHeader header;
    NfcPacket* request;
    NfcPacket* response;
    NfcHistory* history;
};

#ifdef __cplusplus
}
#endif
