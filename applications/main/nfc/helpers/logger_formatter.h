/**
 * @file nfc_supported_cards.h
 * @brief Supported card plugin loader interface.
 *
 * @see nfc_supported_card_plugin.h for instructions on adding a new plugin.
 */
#pragma once

#include <core/string.h>

#include <nfc/nfc.h>

#ifdef __cplusplus
extern "C" {
#endif

/*
typedef struct NfcLoggerFormatter NfcLoggerFormatter;

NfcLoggerFormatter* nfc_logger_formatter_alloc(void);

void nfc_logger_formatter_free(NfcLoggerFormatter* instance); */

void nfc_logger_format(Nfc* nfc);

#ifdef __cplusplus
}
#endif
