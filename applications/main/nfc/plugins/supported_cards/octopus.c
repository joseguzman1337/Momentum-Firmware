// https://github.com/metrodroid/metrodroid/wiki/Octopus

#include "nfc_supported_card_plugin.h"
#include <flipper_application.h>
#include <nfc/protocols/felica/felica.h>
#include <bit_lib.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define TAG "Octopus"

#define SERVICE_CODE_OCTOPUS_IN_LE (0x0117U)

bool octopus_parse(const NfcDevice* device, FuriString* parsed_data) {
    furi_assert(device);
    furi_assert(parsed_data);
    FURI_LOG_I(TAG, "Parsing Octopus card");
    bool parsed = false;

    if(nfc_device_get_protocol(device) != NfcProtocolFelica) return false;

    const FelicaData* felica_data = nfc_device_get_data(device, NfcProtocolFelica);

    for(uint16_t i = 0; i < simple_array_get_count(felica_data->public_blocks); i++) {
        FelicaPublicBlock* public_block = simple_array_get(felica_data->public_blocks, i);
        if(public_block->service_code == SERVICE_CODE_OCTOPUS_IN_LE) {
            uint16_t unsigned_balance = ((uint16_t)public_block->block.data[2] << 8) |
                                        (uint16_t)public_block->block.data[3]; // 0x0000..0xFFFF

            int32_t older_balance_dimes = (int32_t)unsigned_balance - 350;
            int32_t newer_balance_dimes = (int32_t)unsigned_balance - 500;

            uint16_t older_abs_dimes =
                (uint16_t)(older_balance_dimes < 0 ? -older_balance_dimes : older_balance_dimes);
            uint16_t newer_abs_dimes =
                (uint16_t)(newer_balance_dimes < 0 ? -newer_balance_dimes : newer_balance_dimes);

            uint16_t older_dollars = (uint16_t)(older_abs_dimes / 10);
            uint8_t older_dimes = (uint8_t)(older_abs_dimes % 10);

            uint16_t newer_dollars = (uint16_t)(newer_abs_dimes / 10);
            uint8_t newer_dimes = (uint8_t)(newer_abs_dimes % 10);

            furi_string_printf(parsed_data, "\e#Octopus Card\n");
            furi_string_cat_str(
                parsed_data, "::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::\n");

            furi_string_cat_printf(
                parsed_data, "If this card was issued \nbefore 2017 October 1st:\n");
            furi_string_cat_printf(
                parsed_data,
                "Balance: %sHK$ %d.%01d0\n",
                older_balance_dimes < 0 ? "-" : "",
                older_dollars,
                older_dimes);

            furi_string_cat_str(
                parsed_data, "::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::\n");

            furi_string_cat_printf(
                parsed_data, "If this card was issued \nafter 2017 October 1st:\n");
            furi_string_cat_printf(
                parsed_data,
                "Balance: %sHK$ %d.%01d0\n",
                newer_balance_dimes < 0 ? "-" : "",
                newer_dollars,
                newer_dimes);

            furi_string_cat_str(
                parsed_data, "::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::");

            parsed = true;
            break; // Octopus only has one public block
        }
    }

    return parsed;
}

/* Actual implementation of app<>plugin interface */
static const NfcSupportedCardsPlugin octopus_plugin = {
    .protocol = NfcProtocolFelica,
    .verify = NULL,
    .read = NULL,
    .parse = octopus_parse,
};

/* Plugin descriptor to comply with basic plugin specification */
static const FlipperAppPluginDescriptor octopus_plugin_descriptor = {
    .appid = NFC_SUPPORTED_CARD_PLUGIN_APP_ID,
    .ep_api_version = NFC_SUPPORTED_CARD_PLUGIN_API_VERSION,
    .entry_point = &octopus_plugin,
};

/* Plugin entry point - must return a pointer to const descriptor  */
const FlipperAppPluginDescriptor* octopus_plugin_ep(void) {
    return &octopus_plugin_descriptor;
}
