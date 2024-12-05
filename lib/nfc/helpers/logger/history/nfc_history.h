#pragma once

#include "nfc_logger_flags.h"
#include "nfc_history_data_type_i.h"

#include <furi.h>

#ifdef __cplusplus
extern "C" {
#endif

typedef enum {
    NfcLoggerHistoryLayerFilterAll,
    NfcLoggerHistoryLayerFilterTopProtocolOnly,
} NfcLoggerHistoryLayerFilter;

typedef struct NfcHistory NfcHistory;

#ifdef __cplusplus
}
#endif
