#include "nfc_logger.h"

#include <furi_hal_resources.h>
#include <furi_hal_rtc.h>
#include <storage/storage.h>

#include "nfc_transaction.h"

typedef struct {
    NfcProtocol protocol;
    NfcMode mode;
    size_t transactions_count;
} FURI_PACKED NfcTrace;

struct NfcLogger {
    NfcLoggerState state;
    NfcTrace* trace;
    NfcTransaction* transaction;
    uint8_t history_size_max;

    FuriString* filename;
    Storage* storage;
    FuriThread* logger_thread;
    FuriMessageQueue* transaction_queue;
    bool exit;
};
