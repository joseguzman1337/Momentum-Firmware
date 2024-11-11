#pragma once

#include "nfc_transaction.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef struct {
    uint32_t time;
    uint32_t flags;
    size_t data_size;
    uint8_t* data;
} NfcPacket;

struct FURI_PACKED NfcTransaction {
    uint32_t id;
    NfcTransactionType type;
    uint8_t history_count;
    //uint32_t time; ///TODO: optional
    NfcPacket* request;
    NfcPacket* response;
    NfcLoggerHistory* history;
};

#ifdef __cplusplus
}
#endif
