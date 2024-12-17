#pragma once

#include <furi.h>
#include <furi_hal_nfc.h>
#include <stream/file_stream.h>

#include <nfc/protocols/nfc_protocol.h>
#include "transaction/nfc_transaction.h"
#include "history/nfc_history.h"

#ifdef __cplusplus
extern "C" {
#endif

#define NFC_LOG_FOLDER                   "nfc/log"
#define NFC_LOG_TEMP_FILE_NAME           "log_temp.bin"
#define NFC_LOG_FOLDER_PATH              EXT_PATH(NFC_LOG_FOLDER)
#define NFC_LOG_FILE_PATH                NFC_LOG_FOLDER_PATH "/"
#define NFC_LOG_FILE_PATH_BASE(filename) (NFC_LOG_FILE_PATH filename)
#define NFC_LOG_TEMP_FILE_PATH           NFC_LOG_FILE_PATH_BASE(NFC_LOG_TEMP_FILE_NAME)

typedef struct NfcLogger NfcLogger;

typedef enum {
    NfcLoggerTransactionFilterAll,
    NfcLoggerTransactionFilterPayloadOnly,
} NfcLoggerTransactionFilter;

typedef struct {
    NfcLoggerTransactionFilter transaction_filter;
    NfcLoggerHistoryLayerFilter history_filter;
} NfcLoggerFormatFilter;

typedef enum {
    NfcLoggerStateDisabled,
    NfcLoggerStateIdle,
    NfcLoggerStateProcessing,
    NfcLoggerStateStopped,
    NfcLoggerStateError
} NfcLoggerState;

void nfc_logger_config(NfcLogger* instance, bool enabled, const NfcLoggerFormatFilter* filter);
const char* nfc_logger_get_latest_log_filename(NfcLogger* instance);
#ifdef __cplusplus
}
#endif
