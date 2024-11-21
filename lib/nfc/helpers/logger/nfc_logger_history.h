#pragma once

#include "nfc_logger_flags.h"

#include <furi.h>

#ifdef __cplusplus
extern "C" {
#endif

typedef struct {
    NfcProtocol protocol;
    NfcLoggerFlags request_flags;
    NfcLoggerFlags response_flags;
} FURI_PACKED NfcHistoryItem;

typedef struct NfcHistory NfcHistory;

#ifdef __cplusplus
}
#endif
