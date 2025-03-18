#include "type_4_tag_poller_i.h"
#include "type_4_tag_i.h"

#include <bit_lib/bit_lib.h>

#define TAG "Type4TagPoller"

Type4TagError type_4_tag_apdu_trx(Type4TagPoller* instance, BitBuffer* tx_buf, BitBuffer* rx_buf) {
    furi_check(instance);

    bit_buffer_reset(rx_buf);

    Iso14443_4aError iso14443_4a_error =
        iso14443_4a_poller_send_block(instance->iso14443_4a_poller, tx_buf, rx_buf);

    bit_buffer_reset(tx_buf);

    if(iso14443_4a_error != Iso14443_4aErrorNone) {
        return type_4_tag_process_error(iso14443_4a_error);
    }

    size_t response_len = bit_buffer_get_size_bytes(rx_buf);
    if(response_len < TYPE_4_TAG_ISO_STATUS_LEN) {
        return Type4TagErrorWrongFormat;
    }

    const uint8_t success[TYPE_4_TAG_ISO_STATUS_LEN] = {TYPE_4_TAG_ISO_STATUS_SUCCESS};
    uint8_t status[TYPE_4_TAG_ISO_STATUS_LEN] = {
        bit_buffer_get_byte(rx_buf, response_len - 2),
        bit_buffer_get_byte(rx_buf, response_len - 1),
    };
    bit_buffer_set_size_bytes(rx_buf, response_len - 2);

    if(memcmp(status, success, sizeof(status)) == 0) {
        return Type4TagErrorNone;
    } else {
        FURI_LOG_E(TAG, "APDU failed: 0x%02X%02X", status[0], status[1]);
        return Type4TagErrorApduFailed;
    }
}

static Type4TagError type_5_tag_poller_iso_select_name(
    Type4TagPoller* instance,
    const uint8_t* name,
    uint8_t name_len) {
    const uint8_t type_4_tag_iso_select_name_apdu[] = {
        TYPE_4_TAG_ISO_SELECT_CMD,
        TYPE_4_TAG_ISO_SELECT_P1_BY_NAME,
        TYPE_4_TAG_ISO_SELECT_P2_EMPTY,
    };

    bit_buffer_append_bytes(
        instance->tx_buffer,
        type_4_tag_iso_select_name_apdu,
        sizeof(type_4_tag_iso_select_name_apdu));
    bit_buffer_append_byte(instance->tx_buffer, name_len);
    bit_buffer_append_bytes(instance->tx_buffer, name, name_len);

    return type_4_tag_apdu_trx(instance, instance->tx_buffer, instance->rx_buffer);
}

static Type4TagError
    type_5_tag_poller_iso_select_file(Type4TagPoller* instance, uint16_t file_id) {
    const uint8_t type_4_tag_iso_select_file_apdu[] = {
        TYPE_4_TAG_ISO_SELECT_CMD,
        TYPE_4_TAG_ISO_SELECT_P1_BY_EF_ID,
        TYPE_4_TAG_ISO_SELECT_P2_EMPTY,
        sizeof(file_id),
    };
    uint8_t file_id_be[sizeof(file_id)];
    bit_lib_num_to_bytes_be(file_id, sizeof(file_id), file_id_be);

    bit_buffer_append_bytes(
        instance->tx_buffer,
        type_4_tag_iso_select_file_apdu,
        sizeof(type_4_tag_iso_select_file_apdu));
    bit_buffer_append_bytes(instance->tx_buffer, file_id_be, sizeof(file_id_be));

    return type_4_tag_apdu_trx(instance, instance->tx_buffer, instance->rx_buffer);
}

static Type4TagError type_5_tag_poller_iso_read(
    Type4TagPoller* instance,
    uint16_t offset,
    uint16_t length,
    uint8_t* buffer) {
    const uint8_t chunk_max = instance->data->is_tag_specific ?
                                  MIN(instance->data->chunk_max_read, TYPE_4_TAG_CHUNK_LEN) :
                                  TYPE_4_TAG_CHUNK_LEN;
    if(offset + length > TYPE_4_TAG_ISO_READ_P_OFFSET_MAX + chunk_max - sizeof(length)) {
        FURI_LOG_E(TAG, "File too large: %zu bytes", length);
        return Type4TagErrorNotSupported;
    }

    const uint8_t type_4_tag_iso_read_apdu[] = {
        TYPE_4_TAG_ISO_READ_CMD,
    };

    while(length > 0) {
        uint8_t chunk_len = MIN(length, chunk_max);
        uint8_t offset_be[sizeof(offset)];
        bit_lib_num_to_bytes_be(offset, sizeof(offset_be), offset_be);

        bit_buffer_append_bytes(
            instance->tx_buffer, type_4_tag_iso_read_apdu, sizeof(type_4_tag_iso_read_apdu));
        bit_buffer_append_bytes(instance->tx_buffer, offset_be, sizeof(offset_be));
        bit_buffer_append_byte(instance->tx_buffer, chunk_len);

        Type4TagError error =
            type_4_tag_apdu_trx(instance, instance->tx_buffer, instance->rx_buffer);
        if(error != Type4TagErrorNone) {
            return error;
        }
        if(bit_buffer_get_size_bytes(instance->rx_buffer) != chunk_len) {
            FURI_LOG_E(
                TAG,
                "Wrong chunk len: %zu != %zu",
                bit_buffer_get_size_bytes(instance->rx_buffer),
                chunk_len);
            return Type4TagErrorWrongFormat;
        }

        memcpy(buffer, bit_buffer_get_data(instance->rx_buffer), chunk_len);
        buffer += chunk_len;
        offset += chunk_len;
        length -= chunk_len;
    }

    return Type4TagErrorNone;
}

Type4TagError type_4_tag_poller_select_app(Type4TagPoller* instance) {
    furi_check(instance);

    FURI_LOG_D(TAG, "Select application");
    return type_5_tag_poller_iso_select_name(
        instance, type_4_tag_iso_df_name, sizeof(type_4_tag_iso_df_name));
}

Type4TagError type_4_tag_poller_read_cc(Type4TagPoller* instance) {
    furi_check(instance);

    Type4TagError error;

    do {
        FURI_LOG_D(TAG, "Select CC");
        error = type_5_tag_poller_iso_select_file(instance, TYPE_4_TAG_T4T_CC_EF_ID);
        if(error != Type4TagErrorNone) break;

        FURI_LOG_D(TAG, "Read CC len");
        uint16_t cc_len;
        uint8_t cc_len_be[sizeof(cc_len)];
        error = type_5_tag_poller_iso_read(instance, 0, sizeof(cc_len_be), cc_len_be);
        if(error != Type4TagErrorNone) break;
        cc_len = bit_lib_bytes_to_num_be(cc_len_be, sizeof(cc_len_be));

        FURI_LOG_D(TAG, "Read CC");
        uint8_t cc_buf[cc_len];
        error = type_5_tag_poller_iso_read(instance, 0, sizeof(cc_buf), cc_buf);
        if(error != Type4TagErrorNone) break;

        error = type_4_tag_cc_parse(instance->data, cc_buf, sizeof(cc_buf));
        if(error != Type4TagErrorNone) break;
        instance->data->is_tag_specific = true;

        FURI_LOG_D(TAG, "Detected NDEF file ID 0x%04X", instance->data->ndef_file_id);
    } while(false);

    return error;
}

Type4TagError type_4_tag_poller_read_ndef(Type4TagPoller* instance) {
    furi_check(instance);

    Type4TagError error;

    do {
        FURI_LOG_D(TAG, "Select NDEF");
        error = type_5_tag_poller_iso_select_file(instance, instance->data->ndef_file_id);
        if(error != Type4TagErrorNone) break;

        FURI_LOG_D(TAG, "Read NDEF len");
        uint16_t ndef_len;
        uint8_t ndef_len_be[sizeof(ndef_len)];
        error = type_5_tag_poller_iso_read(instance, 0, sizeof(ndef_len_be), ndef_len_be);
        if(error != Type4TagErrorNone) break;
        ndef_len = bit_lib_bytes_to_num_be(ndef_len_be, sizeof(ndef_len_be));

        if(ndef_len == 0) {
            FURI_LOG_D(TAG, "NDEF file is empty");
            break;
        }

        FURI_LOG_D(TAG, "Read NDEF");
        simple_array_init(instance->data->ndef_data, ndef_len);
        uint8_t* ndef_buf = simple_array_get_data(instance->data->ndef_data);
        error = type_5_tag_poller_iso_read(instance, sizeof(ndef_len), ndef_len, ndef_buf);
        if(error != Type4TagErrorNone) break;

        FURI_LOG_D(
            TAG, "Read %hu bytes from NDEF file 0x%04X", ndef_len, instance->data->ndef_file_id);
    } while(false);

    return error;
}

Type4TagError type_4_tag_poller_create_app(Type4TagPoller* instance) {
    UNUSED(instance);
    return Type4TagErrorNotSupported;
}

Type4TagError type_4_tag_poller_create_cc(Type4TagPoller* instance) {
    UNUSED(instance);
    return Type4TagErrorNotSupported;
}

Type4TagError type_4_tag_poller_create_ndef(Type4TagPoller* instance) {
    UNUSED(instance);
    return Type4TagErrorNotSupported;
}

Type4TagError type_4_tag_poller_write_ndef(Type4TagPoller* instance) {
    UNUSED(instance);
    return Type4TagErrorNotSupported;
}
