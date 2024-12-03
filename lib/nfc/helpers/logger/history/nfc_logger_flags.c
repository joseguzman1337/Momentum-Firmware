#include "nfc_logger_flags.h"

#define TAG "NfcLoggerFlags"

typedef void (*NfcLoggerFlagCustomFormatCallback)(FuriString* output);

typedef struct {
    NfcLoggerFlagCustomFormatCallback format;
    ///TODO: introduce here some sort of switch, which will define how default formatting
    ///and custom formatting will behave will they concat or override with each other
    const char* name;
} NfcLoggerFlagDescription;

static void nfc_logger_flag_format_ultralight_command(FuriString* output) {
    furi_string_cat_str(output, "READBLOCK");
    //mf_ultralight get cmd code from payload
    //mf_ultralight parse command, and format with payload
}

static const NfcLoggerFlagDescription ultralight_flag_description[] = {
    [0] = {.name = "CMD", .format = nfc_logger_flag_format_ultralight_command},
    [1] = {.name = "Composite CMD"},
    [2] = {.name = "Reset"},
};

static const NfcLoggerFlagDescription iso14_3a_flag_description[] = {
    [0] = {.name = "CRC_OK"},
    [1] = {.name = "CRC_BAD"},
    [2] = {.name = "Activated"},
    [3] = {.name = "HALT"},
    [4] = {.name = "Field Off"},
};

/* static const NfcLoggerFlagDescription felica_flag_description[] = {
    [0] = {.name = "FELICA_CRC_OK"},
    [1] = {.name = "FELICA_CRC_BAD"},
}; */

static const NfcLoggerFlagDescription nfc_hal_flag_description[] = {
    [0] = {.name = "OscOn"},
    [1] = {.name = "Field On"},
    [2] = {.name = "Field Off"},
    [3] = {.name = "Activate"},
    [4] = {.name = "TxStart"},
    [5] = {.name = "TxEnd"},
    [6] = {.name = "RxStart"},
    [7] = {.name = "RxEnd"},
    [8] = {.name = "Collision"},
    [9] = {.name = "Frame Wait Timer Expired"},
    [10] = {.name = "Block Tx Timer Expired"},
    [11] = {.name = "Timeout"},
    [12] = {.name = "Abort Request"},
};

static const NfcLoggerFlagDescription*
    nfc_flags_get_description_for_protocol(NfcProtocol protocol, size_t* array_size) {
    const NfcLoggerFlagDescription* flag_description_array = NULL;
    *array_size = 0;
    switch(protocol) {
    case NfcProtocolInvalid:
        flag_description_array = nfc_hal_flag_description;
        *array_size = COUNT_OF(nfc_hal_flag_description);
        break;
    case NfcProtocolIso14443_3a:
        flag_description_array = iso14_3a_flag_description;
        *array_size = COUNT_OF(iso14_3a_flag_description);
        break;
    case NfcProtocolMfUltralight:
        flag_description_array = ultralight_flag_description;
        *array_size = COUNT_OF(ultralight_flag_description);
        break;
    default:
        break;
    }
    return flag_description_array;
}

void nfc_logger_flag_parse(NfcProtocol protocol, uint32_t flags, FuriString* output) {
    size_t size = 0;
    const NfcLoggerFlagDescription* flag_description =
        nfc_flags_get_description_for_protocol(protocol, &size);

    uint8_t flags_cnt = 0;
    for(size_t i = 0; i < size; i++) {
        uint32_t flag_mask = (1 << i);
        if(flags & flag_mask) {
            const NfcLoggerFlagDescription* fd = &flag_description[i];
            furi_string_cat_printf(output, (flags_cnt > 0) ? ", %s" : "%s", fd->name);

            if(fd->format) {
                fd->format(output);
            }
            flags_cnt++;
        }
    }
}
