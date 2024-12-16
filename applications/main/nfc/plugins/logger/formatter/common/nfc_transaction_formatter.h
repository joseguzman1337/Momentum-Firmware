#pragma once

#include <furi.h>
#include "../nfc_formatter_context.h"
#include "nfc/helpers/logger/nfc_trace_data_type_i.h"
#include "nfc/helpers/logger/nfc_transaction.h"

#ifdef __cplusplus
extern "C" {
#endif

void nfc_format_transaction(
    const NfcFormatter* instance,
    const NfcTransaction* transaction,
    FuriString* output);
#ifdef __cplusplus
}
#endif
