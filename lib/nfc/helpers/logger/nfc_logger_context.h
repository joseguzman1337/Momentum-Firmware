#pragma once

#include "nfc_logger_i.h"

#include <furi_hal_rtc.h>
#include <storage/storage.h>
#include <stream/file_stream.h>
#include <toolbox/path.h>

#include "nfc_transaction.h"
#include "nfc_trace_data_type_i.h"

#ifdef __cplusplus
extern "C" {
#endif

struct NfcLogger {
    NfcLoggerState state;
    NfcProtocol protocol;
    NfcTrace* trace;
    NfcTransaction* transaction;
    uint8_t max_chain_size;
    uint8_t history_size_bytes;

    uint32_t dwt_cnt_prev;
    uint32_t dwt_ovf_cnt;
    uint32_t dwt_second_per_ovf;
    uint32_t dwt_cycles_per_timeout_delay;
    FuriMutex* dwt_mutex;

    NfcLoggerFormatFilter filter;
    FuriString* filename;
    Storage* storage;
    FuriThread* logger_thread;
    FuriMessageQueue* transaction_queue;
    bool exit;
};

#ifdef __cplusplus
}
#endif
