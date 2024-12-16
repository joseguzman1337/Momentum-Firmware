/**
 *
 * @note the APPID field MUST end with `_parser` so the applicaton would know that this particular file
 * is a supported card plugin.
 *
 * @see nfc_supported_cards.h
 */
#pragma once

#include <furi/core/string.h>

#include <nfc/nfc.h>
#include <nfc/nfc_device.h>

/**
 * @brief Unique string identifier for supported card plugins.
 */
#define NFC_LOGGER_FORMATTER_PLUGIN_APP_ID "NfcLoggerFormatterPlugin"

/**
 * @brief Currently supported plugin API version.
 */
#define NFC_LOGGER_FORMATTER_PLUGIN_API_VERSION 1

typedef void (*NfcLoggerFormatterPluginFormat)(Nfc* nfc);
/**
 * @brief Supported card plugin interface.
 *
 * For a minimally functional plugin, only the parse() function must be implemented.
 */
typedef struct {
    NfcLoggerFormatterPluginFormat format;
} NfcLoggerFormatterPlugin;
