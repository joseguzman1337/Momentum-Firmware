#include "felica.h"

#include <furi.h>

#include <nfc/nfc_common.h>

#define FELICA_PROTOCOL_NAME "FeliCa"
#define FELICA_DEVICE_NAME "FeliCa"

#define FELICA_DATA_FORMAT_VERSION "Data format version"
#define FELICA_MANUFACTURE_ID "Manufacture id"
#define FELICA_MANUFACTURE_PARAMETER "Manufacture parameter"

static const uint32_t felica_data_format_version = 1;

const NfcDeviceBase nfc_device_felica = {
    .protocol_name = FELICA_PROTOCOL_NAME,
    .alloc = (NfcDeviceAlloc)felica_alloc,
    .free = (NfcDeviceFree)felica_free,
    .reset = (NfcDeviceReset)felica_reset,
    .copy = (NfcDeviceCopy)felica_copy,
    .verify = (NfcDeviceVerify)felica_verify,
    .load = (NfcDeviceLoad)felica_load,
    .save = (NfcDeviceSave)felica_save,
    .is_equal = (NfcDeviceEqual)felica_is_equal,
    .get_name = (NfcDeviceGetName)felica_get_device_name,
    .get_uid = (NfcDeviceGetUid)felica_get_uid,
    .set_uid = (NfcDeviceSetUid)felica_set_uid,
    .get_base_data = (NfcDeviceGetBaseData)felica_get_base_data,
};

FelicaData* felica_alloc(void) {
    FelicaData* data = malloc(sizeof(FelicaData));
    return data;
}

void felica_free(FelicaData* data) {
    furi_check(data);

    free(data);
}

void felica_reset(FelicaData* data) {
    furi_check(data);

    memset(data, 0, sizeof(FelicaData));
}

void felica_copy(FelicaData* data, const FelicaData* other) {
    furi_check(data);
    furi_check(other);

    *data = *other;
}

bool felica_verify(FelicaData* data, const FuriString* device_type) {
    UNUSED(data);
    UNUSED(device_type);

    return false;
}

bool felica_load(FelicaData* data, FlipperFormat* ff, uint32_t version) {
    furi_check(data);
    furi_check(ff);

    bool parsed = false;

    do {
        if(version < NFC_UNIFIED_FORMAT_VERSION) break;

        uint32_t data_format_version = 0;
        if(!flipper_format_read_uint32(ff, FELICA_DATA_FORMAT_VERSION, &data_format_version, 1))
            break;
        if(data_format_version != felica_data_format_version) break;
        if(!flipper_format_read_hex(ff, FELICA_MANUFACTURE_ID, data->idm.data, FELICA_IDM_SIZE))
            break;
        if(!flipper_format_read_hex(
               ff, FELICA_MANUFACTURE_PARAMETER, data->pmm.data, FELICA_PMM_SIZE))
            break;

        parsed = true;
    } while(false);

    return parsed;
}

bool felica_save(const FelicaData* data, FlipperFormat* ff) {
    furi_check(data);
    furi_check(ff);

    bool saved = false;

    do {
        if(!flipper_format_write_comment_cstr(ff, FELICA_PROTOCOL_NAME " specific data")) break;
        if(!flipper_format_write_uint32(
               ff, FELICA_DATA_FORMAT_VERSION, &felica_data_format_version, 1))
            break;
        if(!flipper_format_write_hex(ff, FELICA_MANUFACTURE_ID, data->idm.data, FELICA_IDM_SIZE))
            break;
        if(!flipper_format_write_hex(
               ff, FELICA_MANUFACTURE_PARAMETER, data->pmm.data, FELICA_PMM_SIZE))
            break;

        saved = true;
    } while(false);

    return saved;
}

bool felica_is_equal(const FelicaData* data, const FelicaData* other) {
    furi_check(data);
    furi_check(other);

    return memcmp(data, other, sizeof(FelicaData)) == 0;
}

const char* felica_get_device_name(const FelicaData* data, NfcDeviceNameType name_type) {
    UNUSED(data);
    UNUSED(name_type);

    return FELICA_DEVICE_NAME;
}

const uint8_t* felica_get_uid(const FelicaData* data, size_t* uid_len) {
    furi_check(data);

    // Consider Manufacturer ID as UID
    if(uid_len) {
        *uid_len = FELICA_IDM_SIZE;
    }

    return data->idm.data;
}

bool felica_set_uid(FelicaData* data, const uint8_t* uid, size_t uid_len) {
    furi_check(data);
    furi_check(uid);

    // Consider Manufacturer ID as UID
    const bool uid_valid = uid_len == FELICA_IDM_SIZE;
    if(uid_valid) {
        memcpy(data->idm.data, uid, uid_len);
    }

    return uid_valid;
}

FelicaData* felica_get_base_data(const FelicaData* data) {
    UNUSED(data);
    furi_crash("No base data");
}

static void felica_reverse_copy_block(const uint8_t* array, uint8_t* reverse_array) {
    furi_assert(array);
    furi_assert(reverse_array);

    for(int i = 0; i < 8; i++) {
        reverse_array[i] = array[7 - i];
    }
}

void felica_calculate_session_key(
    mbedtls_des3_context* ctx,
    const uint8_t* ck,
    const uint8_t* rc,
    uint8_t* out) {
    furi_check(ctx);
    furi_check(ck);
    furi_check(rc);
    furi_check(out);

    uint8_t iv[8];
    memset(iv, 0, 8);

    uint8_t ck_reversed[16];
    felica_reverse_copy_block(ck, ck_reversed);
    felica_reverse_copy_block(ck + 8, ck_reversed + 8);

    uint8_t rc_reversed[16];
    felica_reverse_copy_block(rc, rc_reversed);
    felica_reverse_copy_block(rc + 8, rc_reversed + 8);

    mbedtls_des3_set2key_enc(ctx, ck_reversed);
    mbedtls_des3_crypt_cbc(ctx, MBEDTLS_DES_ENCRYPT, FELICA_DATA_BLOCK_SIZE, iv, rc_reversed, out);
}

static bool felica_calculate_mac(
    mbedtls_des3_context* ctx,
    const uint8_t* session_key,
    const uint8_t* rc,
    const uint8_t* first_block,
    const uint8_t* data,
    const size_t length,
    uint8_t* mac) {
    furi_check((length % 8) == 0);

    uint8_t reverse_data[8];
    uint8_t iv[8];
    uint8_t out[8];
    mbedtls_des3_set2key_enc(ctx, session_key);

    felica_reverse_copy_block(rc, iv);
    felica_reverse_copy_block(first_block, reverse_data);
    uint8_t i = 0;
    bool error = false;
    do {
        if(mbedtls_des3_crypt_cbc(ctx, MBEDTLS_DES_ENCRYPT, 8, iv, reverse_data, out) == 0) {
            memcpy(iv, out, sizeof(iv));
            felica_reverse_copy_block(data + i, reverse_data);
            i += 8;
        } else {
            error = true;
            break;
        }
    } while(i <= length);

    if(!error) {
        felica_reverse_copy_block(out, mac);
    }
    return !error;
}

static void felica_prepare_first_block(
    FelicaMACType operation_type,
    const uint8_t* blocks,
    const uint8_t block_count,
    uint8_t* out) {
    furi_check(blocks);
    furi_check(out);
    if(operation_type == FelicaMACTypeRead) {
        memset(out, 0xFF, 8);
        for(uint8_t i = 0, j = 0; i < block_count; i++, j += 2) {
            out[j] = blocks[i];
            out[j + 1] = 0;
        }
    } else {
        furi_check(block_count == 4);
        memset(out, 0, 8);
        out[0] = blocks[0];
        out[1] = blocks[1];
        out[2] = blocks[2];
        out[4] = blocks[3];
        out[6] = FELICA_BLOCK_INDEX_MAC_A;
    }
}

bool felica_check_mac(
    mbedtls_des3_context* ctx,
    const uint8_t* session_key,
    const uint8_t* rc,
    const uint8_t* blocks,
    const uint8_t block_count,
    uint8_t* data) {
    furi_check(ctx);
    furi_check(session_key);
    furi_check(rc);
    furi_check(blocks);
    furi_check(data);

    uint8_t mac[8];
    felica_calculate_mac_read(ctx, session_key, rc, blocks, block_count, data, mac);

    uint8_t mac_offset = FELICA_DATA_BLOCK_SIZE * (block_count - 1);
    uint8_t* mac_ptr = data + mac_offset;
    return !memcmp(mac, mac_ptr, 8);
}

void felica_calculate_mac_read(
    mbedtls_des3_context* ctx,
    const uint8_t* session_key,
    const uint8_t* rc,
    const uint8_t* blocks,
    const uint8_t block_count,
    const uint8_t* data,
    uint8_t* mac) {
    furi_check(ctx);
    furi_check(session_key);
    furi_check(rc);
    furi_check(blocks);
    furi_check(data);
    furi_check(mac);

    uint8_t first_block[8];
    felica_prepare_first_block(FelicaMACTypeRead, blocks, block_count, first_block);
    uint8_t data_size_without_mac = FELICA_DATA_BLOCK_SIZE * (block_count - 1);
    felica_calculate_mac(ctx, session_key, rc, first_block, data, data_size_without_mac, mac);
}

void felica_calculate_mac_write(
    mbedtls_des3_context* ctx,
    const uint8_t* session_key,
    const uint8_t* rc,
    const uint8_t* wcnt,
    const uint8_t* data,
    uint8_t* mac) {
    furi_check(ctx);
    furi_check(session_key);
    furi_check(rc);
    furi_check(wcnt);
    furi_check(data);
    furi_check(mac);

    const uint8_t WCNT_length = 3;
    uint8_t block_data[WCNT_length + 1];
    uint8_t first_block[8];

    memcpy(block_data, wcnt, WCNT_length);
    block_data[3] = FELICA_BLOCK_INDEX_STATE;
    felica_prepare_first_block(FelicaMACTypeWrite, block_data, WCNT_length + 1, first_block);

    uint8_t session_swapped[FELICA_DATA_BLOCK_SIZE];
    memcpy(session_swapped, session_key + 8, 8);
    memcpy(session_swapped + 8, session_key, 8);
    felica_calculate_mac(ctx, session_swapped, rc, first_block, data, FELICA_DATA_BLOCK_SIZE, mac);
}

void felica_write_directory_tree(const FelicaData* data, FuriString* str) {
    furi_check(data);
    furi_check(str);

    furi_string_cat_str(str, "\n");

    uint16_t area_last_stack[8];
    uint8_t depth = 0;

    size_t area_iter = 0;
    const size_t area_count = simple_array_get_count(data->areas);
    const size_t service_count = simple_array_get_count(data->services);

    for(size_t svc_idx = 0; svc_idx < service_count; ++svc_idx) {
        while(area_iter < area_count) {
            const FelicaArea* next_area = simple_array_get(data->areas, area_iter);
            if(next_area->first_idx != svc_idx) break;

            for(uint8_t i = 0; i < depth - 1; ++i)
                furi_string_cat_printf(str, "| ");
            furi_string_cat_printf(str, depth ? "|" : "");
            furi_string_cat_printf(str, "- AREA_%04X/\n", next_area->code >> 6);

            area_last_stack[depth++] = next_area->last_idx;
            area_iter++;
        }

        const FelicaService* service = simple_array_get(data->services, svc_idx);
        bool is_public = (service->attr & FELICA_SERVICE_ATTRIBUTE_UNAUTH_READ) != 0;

        for(uint8_t i = 0; i < depth - 1; ++i)
            furi_string_cat_printf(str, is_public ? ": " : "| ");
        furi_string_cat_printf(str, is_public ? ":" : "|");
        furi_string_cat_printf(str, "- serv_%04X\n", service->code);

        if(depth && svc_idx >= area_last_stack[depth - 1]) depth--;
    }
}

void felica_get_workflow_type(FelicaData* data) {
    // Reference: Proxmark3 repo
    uint8_t rom_type = data->pmm.data[0];
    uint8_t workflow_type = data->pmm.data[1];
    if(workflow_type <= 0x48) {
        // More liberal check because most of these should be treated as FeliCa Standard, regardless of mobile or not.
        data->workflow_type = FelicaStandard;
    } else {
        switch(workflow_type) {
        case 0xA2:
            data->workflow_type = FelicaStandard;
            break;
        case 0xF0:
        case 0xF1:
        case 0xF2: // 0xF2 => FeliCa Link RC-S967 in Lite-S Mode or Lite-S HT Mode
            data->workflow_type = FelicaLite;
            break;
        case 0xE1: // Felica Link
        case 0xE0: // Felica Plug
            data->workflow_type = FelicaUnknown;
            break;
        case 0xFF:
            if(rom_type == 0xFF) {
                data->workflow_type = FelicaUnknown; // Felica Link
            }
            break;
        default:
            data->workflow_type = FelicaUnknown;
            break;
        }
    }
}

void felica_get_ic_name(const FelicaData* data, FuriString* ic_name) {
    // Reference: Proxmark3 repo
    uint8_t rom_type = data->pmm.data[0];
    uint8_t ic_type = data->pmm.data[1];

    switch(ic_type) {
        // FeliCa Standard Products:
        // odd findings
    case 0x00:
        furi_string_set_str(ic_name, "FeliCa Standard RC-S830");
        break;
    case 0x01:
        furi_string_set_str(ic_name, "FeliCa Standard RC-S915");
        break;
    case 0x02:
        furi_string_set_str(ic_name, "FeliCa Standard RC-S919");
        break;
    case 0x06:
    case 0x07:
        furi_string_set_str(ic_name, "FeliCa Mobile IC,\nChip V1.0");
        break;
    case 0x08:
        furi_string_set_str(ic_name, "FeliCa Standard RC-S952");
        break;
    case 0x09:
        furi_string_set_str(ic_name, "FeliCa Standard RC-S953");
        break;
    case 0x0B:
        furi_string_set_str(ic_name, "FeliCa Standard RC-S9X4,\nJapan Transit IC");
        break;
    case 0x0C:
        furi_string_set_str(ic_name, "FeliCa Standard RC-S954");
        break;
    case 0x0D:
        furi_string_set_str(ic_name, "FeliCa Standard RC-S960");
        break;
    case 0x10:
    case 0x11:
    case 0x12:
    case 0x13:
        furi_string_set_str(ic_name, "FeliCa Mobile IC,\nChip V2.0");
        break;
    case 0x14:
    case 0x15:
        furi_string_set_str(ic_name, "FeliCa Mobile IC,\nChip V3.0");
        break;
    case 0x16:
        furi_string_set_str(ic_name, "FeliCa Mobile IC,\nJapan Transit IC");
        break;
    case 0x17:
        furi_string_set_str(ic_name, "FeliCa Mobile IC,\nChip V4.0");
        break;
    case 0x18:
    case 0x19:
    case 0x1A:
    case 0x1B:
    case 0x1C:
    case 0x1D:
    case 0x1E:
    case 0x1F:
        furi_string_set_str(ic_name, "FeliCa Mobile IC,\nChip V4.1");
        break;
    case 0x20:
        furi_string_set_str(ic_name, "FeliCa Standard RC-S962");
        // RC-S962 has been extensively found in Japan Transit ICs, despite model number not ending in 4
        break;
    case 0x31:
        furi_string_set_str(ic_name, "FeliCa Standard RC-S104,\nJapan Transit IC");
        break;
    case 0x32:
        furi_string_set_str(ic_name, "FeliCa Standard RC-SA00/1");
        break;
    case 0x33:
        furi_string_set_str(ic_name, "FeliCa Standard RC-SA00/2");
        break;
    case 0x34:
        furi_string_set_str(ic_name, "FeliCa Standard RC-SA01/1");
        break;
    case 0x35:
        furi_string_set_str(ic_name, "FeliCa Standard RC-SA01/2");
        break;
    case 0x36:
        furi_string_set_str(ic_name, "FeliCa Standard RC-SA04/1,\nJapan Transit IC");
        break;
    case 0x3B:
        furi_string_set_str(ic_name, "FeliCa Standard Unknown IC,\nOctopus x T-Union Dual Tech");
        break;
    case 0x3E:
        furi_string_set_str(ic_name, "FeliCa Standard RC-SA08/1");
        break;
    case 0x43:
        furi_string_set_str(ic_name, "FeliCa Standard RC-SA24/1");
        break;
    case 0x44:
        furi_string_set_str(ic_name, "FeliCa Standard RC-SA20/1");
        break;
    case 0x45:
        furi_string_set_str(ic_name, "FeliCa Standard RC-SA20/2");
        break;
    case 0x46:
        furi_string_set_str(ic_name, "FeliCa Standard RC-SA21/2");
        break;
    case 0x47:
        furi_string_set_str(ic_name, "FeliCa Standard RC-SA24/1x1");
        break;
    case 0x48:
        furi_string_set_str(ic_name, "FeliCa Standard RC-SA21/2x1");
        break;
    case 0xA2:
        furi_string_set_str(ic_name, "FeliCa Standard RC-SA14");
        break;
    // NFC Dynamic Tag (FeliCa Plug) Products:
    case 0xE0:
        furi_string_set_str(ic_name, "FeliCa Plug RC-S926,\nNFC Dynamic Tag");
        break;
    case 0xE1:
        furi_string_set_str(ic_name, "FeliCa Link RC-S967,\nPlug Mode");
        break;
    case 0xF0:
        furi_string_set_str(ic_name, "FeliCa Lite RC-S965");
        break;
    case 0xF1:
        furi_string_set_str(ic_name, "FeliCa Lite-S RC-S966");
        break;
    case 0xF2:
        furi_string_set_str(ic_name, "FeliCa Link RC-S967,\nLite-S Mode or Lite-S HT Mode");
        break;
    case 0xFF:
        if(rom_type == 0xFF) { // from FeliCa Link User's Manual
            furi_string_set_str(ic_name, "FeliCa Link RC-S967,\nNFC-DEP Mode");
        }
        break;
    default:
        furi_string_printf(
            ic_name,
            "Unknown IC %02X ROM %02X:\nPlease submit an issue on\nGitHub and help us identify.",
            ic_type,
            rom_type);
        break;
    }
}

void felica_service_get_attribute_string(const FelicaService* service, FuriString* str) {
    furi_check(service);
    furi_check(str);

    bool is_public = (service->attr & FELICA_SERVICE_ATTRIBUTE_UNAUTH_READ) != 0;
    furi_string_cat_str(str, is_public ? "| Public  " : "| Private ");

    bool is_purse = (service->attr & FELICA_SERVICE_ATTRIBUTE_PURSE) != 0;
    // Subfield bitwise attributes are applicable depending on is PURSE or not

    if(is_purse) {
        furi_string_cat_str(str, "| Purse  |");
        switch((service->attr & FELICA_SERVICE_ATTRIBUTE_PURSE_SUBFIELD) >> 1) {
        case 0:
            furi_string_cat_str(str, " Direct     |");
            break;
        case 1:
            furi_string_cat_str(str, " Cashback   |");
            break;
        case 2:
            furi_string_cat_str(str, " Decrement  |");
            break;
        case 3:
            furi_string_cat_str(str, " Read Only  |");
            break;
        default:
            furi_string_cat_str(str, " Unknown    |");
            break;
        }
    } else {
        bool is_random = (service->attr & FELICA_SERVICE_ATTRIBUTE_RANDOM_ACCESS) != 0;
        furi_string_cat_str(str, is_random ? "| Random |" : "| Cyclic |");
        bool is_readonly = (service->attr & FELICA_SERVICE_ATTRIBUTE_READ_ONLY) != 0;
        furi_string_cat_str(str, is_readonly ? " Read Only  |" : " Read/Write |");
    }
}
