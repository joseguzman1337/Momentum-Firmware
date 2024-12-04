#pragma once

#include <furi.h>
#include <nfc.h>

#include "nfc/helpers/logger/nfc_trace_data_type_i.h"
#include "nfc/helpers/logger/nfc_transaction.h"

#include "nfc/helpers/logger/table.h"
#ifdef __cplusplus
extern "C" {
#endif

typedef struct {
    uint8_t table_columns_cnt;
    NfcLoggerFormatFilter filter;
    Table* table;
} NfcFormatter;

void nfc_history_data_format(
    NfcProtocol protocol,
    NfcMode mode,
    const NfcHistoryData* data,
    FuriString* output);

NfcFormatter* nfc_formatter_alloc(void);
void nfc_formatter_free(NfcFormatter* instance);

void nfc_format_table_header(const NfcFormatter* formatter, FuriString* output);

void nfc_format_trace(
    const NfcFormatter* instance,
    const char* file_name,
    const NfcTrace* trace,
    FuriString* output);

void nfc_format_transaction(
    const NfcFormatter* instance,
    const NfcTransaction* transaction,
    FuriString* output);
#ifdef __cplusplus
}
#endif
