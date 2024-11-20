#pragma once

#include "nfc_logger_history.h"

#ifdef __cplusplus
extern "C" {
#endif

void nfc_histroy_format_crc_status(
    NfcLoggerHistory* history,
    size_t history_cnt,
    FuriString* crc_status_str);

#ifdef __cplusplus
}
#endif
