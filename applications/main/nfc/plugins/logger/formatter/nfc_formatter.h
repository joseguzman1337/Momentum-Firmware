#pragma once

#include <furi.h>
#include <nfc.h>

#include "nfc_formatter_context.h"
#include <nfc/helpers/logger/nfc_trace_data_type_i.h>
#include <nfc/helpers/logger/nfc_transaction.h>

#include "../nfc_logger_formatter_plugin.h"

#ifdef __cplusplus
extern "C" {
#endif

NfcFormatter* nfc_formatter_alloc(void);
void nfc_formatter_free(NfcFormatter* instance);

void nfc_format_table_header(const NfcFormatter* formatter, FuriString* output);

void nfc_format_trace(
    NfcFormatter* instance,
    const char* file_name,
    const NfcTrace* trace,
    FuriString* output);

void nfc_formatter_format(
    NfcFormatter* instance,
    const NfcTransaction* transaction,
    FuriString* output);
#ifdef __cplusplus
}
#endif
