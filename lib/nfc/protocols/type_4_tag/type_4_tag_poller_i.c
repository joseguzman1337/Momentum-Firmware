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
        return Type4TagErrorUnknown;
    }
}

Type4TagError type_4_tag_poller_select_app(Type4TagPoller* instance) {
    furi_check(instance);

    FURI_LOG_D(TAG, "Select application");
    const uint8_t type_4_tag_select_app_apdu[] = {
        TYPE_4_TAG_ISO_SELECT_CMD,
        TYPE_4_TAG_ISO_SELECT_P1_BY_DF_NAME,
        TYPE_4_TAG_ISO_SELECT_P2_EMPTY,
        TYPE_4_TAG_ISO_APP_NAME_LEN,
        TYPE_4_TAG_ISO_APP_NAME,
        TYPE_4_TAG_ISO_SELECT_LE_EMPTY,
    };

    bit_buffer_append_bytes(
        instance->tx_buffer, type_4_tag_select_app_apdu, sizeof(type_4_tag_select_app_apdu));

    return type_4_tag_apdu_trx(instance, instance->tx_buffer, instance->rx_buffer);
}

Type4TagError type_4_tag_poller_read_cc(Type4TagPoller* instance) {
    furi_check(instance);

    Type4TagError error;

    do {
        FURI_LOG_D(TAG, "Select CC");
        const uint8_t type_4_tag_select_cc_apdu[] = {
            TYPE_4_TAG_ISO_SELECT_CMD,
            TYPE_4_TAG_ISO_SELECT_P1_BY_ID,
            TYPE_4_TAG_ISO_SELECT_P2_EMPTY,
            TYPE_4_TAG_T4T_CC_FILE_ID_LEN,
            TYPE_4_TAG_T4T_CC_FILE_ID,
            TYPE_4_TAG_ISO_SELECT_LE_EMPTY,
        };

        bit_buffer_append_bytes(
            instance->tx_buffer, type_4_tag_select_cc_apdu, sizeof(type_4_tag_select_cc_apdu));

        error = type_4_tag_apdu_trx(instance, instance->tx_buffer, instance->rx_buffer);
        if(error != Type4TagErrorNone) break;

        FURI_LOG_D(TAG, "Read CC");
        const uint8_t type_4_tag_read_cc_apdu[] = {
            TYPE_4_TAG_ISO_READ_CMD,
            TYPE_4_TAG_ISO_READ_P1_EMPTY,
            TYPE_4_TAG_ISO_READ_P_BEGINNING,
            TYPE_4_TAG_ISO_READ_LE_FULL,
        };

        bit_buffer_append_bytes(
            instance->tx_buffer, type_4_tag_read_cc_apdu, sizeof(type_4_tag_read_cc_apdu));

        error = type_4_tag_apdu_trx(instance, instance->tx_buffer, instance->rx_buffer);
        if(error != Type4TagErrorNone) break;

        const Type4TagCc* cc = (const Type4TagCc*)bit_buffer_get_data(instance->rx_buffer);
        if(cc->t4t_vno != TYPE_4_TAG_T4T_CC_VNO) {
            FURI_LOG_E(TAG, "Unsupported T4T version");
            error = Type4TagErrorNotSupported;
            break;
        }

        const Type4TagCcTlv* tlv = cc->tlv;
        const Type4TagCcTlvNdefFileCtrl* ndef_file_ctrl = NULL;
        while((void*)tlv < (void*)cc + cc->len) {
            if(tlv->type == Type4TagCcTlvTypeNdefFileCtrl) {
                ndef_file_ctrl = &tlv->value.ndef_file_ctrl;
                break;
            }

            if(tlv->len < 0xFF) {
                tlv = (void*)&tlv->value + tlv->len;
            } else {
                uint16_t len = bit_lib_bytes_to_num_be((void*)&tlv->len + 1, sizeof(uint16_t));
                tlv = (void*)&tlv->value + sizeof(len) + len;
            }
        }
        if(!ndef_file_ctrl) {
            FURI_LOG_E(TAG, "No NDEF file ctrl TLV");
            error = Type4TagErrorWrongFormat;
            break;
        }

        instance->data->is_tag_specific = true;
        instance->data->t4t_version.value = cc->t4t_vno;
        instance->data->chunk_max_read = bit_lib_bytes_to_num_be((void*)&cc->mle, sizeof(cc->mle));
        instance->data->chunk_max_write =
            bit_lib_bytes_to_num_be((void*)&cc->mlc, sizeof(cc->mlc));
        instance->data->ndef_file_id = bit_lib_bytes_to_num_be(
            (void*)&ndef_file_ctrl->file_id, sizeof(ndef_file_ctrl->file_id));
        instance->data->ndef_max_len =
            bit_lib_bytes_to_num_be(
                (void*)&ndef_file_ctrl->max_len, sizeof(ndef_file_ctrl->max_len)) -
            sizeof(uint16_t);
        instance->data->ndef_read_lock = ndef_file_ctrl->read_perm;
        instance->data->ndef_write_lock = ndef_file_ctrl->write_perm;

        FURI_LOG_D(TAG, "Detected NDEF file ID 0x%04X", instance->data->ndef_file_id);
    } while(false);

    return error;
}

Type4TagError type_4_tag_poller_read_ndef(Type4TagPoller* instance) {
    furi_check(instance);

    Type4TagError error;

    do {
        FURI_LOG_D(TAG, "Select NDEF");
        const uint8_t type_4_tag_select_ndef_apdu_1[] = {
            TYPE_4_TAG_ISO_SELECT_CMD,
            TYPE_4_TAG_ISO_SELECT_P1_BY_ID,
            TYPE_4_TAG_ISO_SELECT_P2_EMPTY,
            sizeof(instance->data->ndef_file_id),
        };
        uint8_t ndef_file_id_be[sizeof(instance->data->ndef_file_id)];
        bit_lib_num_to_bytes_be(
            instance->data->ndef_file_id, sizeof(instance->data->ndef_file_id), ndef_file_id_be);
        const uint8_t type_4_tag_select_ndef_apdu_2[] = {
            TYPE_4_TAG_ISO_SELECT_LE_EMPTY,
        };

        bit_buffer_append_bytes(
            instance->tx_buffer,
            type_4_tag_select_ndef_apdu_1,
            sizeof(type_4_tag_select_ndef_apdu_1));
        bit_buffer_append_bytes(instance->tx_buffer, ndef_file_id_be, sizeof(ndef_file_id_be));
        bit_buffer_append_bytes(
            instance->tx_buffer,
            type_4_tag_select_ndef_apdu_2,
            sizeof(type_4_tag_select_ndef_apdu_2));

        error = type_4_tag_apdu_trx(instance, instance->tx_buffer, instance->rx_buffer);
        if(error != Type4TagErrorNone) break;

        FURI_LOG_D(TAG, "Read NDEF len");
        uint16_t ndef_len;
        const uint8_t type_4_tag_read_ndef_len_apdu[] = {
            TYPE_4_TAG_ISO_READ_CMD,
            TYPE_4_TAG_ISO_READ_P1_EMPTY,
            TYPE_4_TAG_ISO_READ_P_BEGINNING,
            sizeof(ndef_len),
        };

        bit_buffer_append_bytes(
            instance->tx_buffer,
            type_4_tag_read_ndef_len_apdu,
            sizeof(type_4_tag_read_ndef_len_apdu));

        error = type_4_tag_apdu_trx(instance, instance->tx_buffer, instance->rx_buffer);
        if(error != Type4TagErrorNone) break;

        ndef_len =
            bit_lib_bytes_to_num_be(bit_buffer_get_data(instance->rx_buffer), sizeof(ndef_len));
        if(ndef_len == 0) {
            FURI_LOG_D(TAG, "NDEF file is empty");
            break;
        }
        uint8_t chunk_max = MIN(instance->data->chunk_max_read, TYPE_4_TAG_ISO_RW_CHUNK_LEN);
        if(ndef_len > TYPE_4_TAG_ISO_READ_P_OFFSET_MAX + chunk_max - sizeof(ndef_len)) {
            FURI_LOG_E(TAG, "NDEF file too long: %zu bytes", ndef_len);
            error = Type4TagErrorNotSupported;
            break;
        }
        simple_array_init(instance->data->ndef_data, ndef_len);

        FURI_LOG_D(TAG, "Read NDEF");
        const uint8_t type_4_tag_read_ndef_apdu_1[] = {
            TYPE_4_TAG_ISO_READ_CMD,
        };

        uint16_t ndef_pos = 0;
        uint8_t* ndef_data = simple_array_get_data(instance->data->ndef_data);
        while(ndef_len > 0) {
            uint8_t chunk_len = MIN(ndef_len, chunk_max);
            uint8_t ndef_pos_be[sizeof(ndef_pos)];
            bit_lib_num_to_bytes_be(sizeof(ndef_len) + ndef_pos, sizeof(ndef_pos_be), ndef_pos_be);

            bit_buffer_append_bytes(
                instance->tx_buffer,
                type_4_tag_read_ndef_apdu_1,
                sizeof(type_4_tag_read_ndef_apdu_1));
            bit_buffer_append_bytes(instance->tx_buffer, ndef_pos_be, sizeof(ndef_pos_be));
            bit_buffer_append_byte(instance->tx_buffer, chunk_len);

            error = type_4_tag_apdu_trx(instance, instance->tx_buffer, instance->rx_buffer);
            if(error != Type4TagErrorNone) break;
            if(bit_buffer_get_size_bytes(instance->rx_buffer) != chunk_len) {
                FURI_LOG_E(
                    TAG,
                    "Wrong NDEF chunk len: %zu != %zu",
                    bit_buffer_get_size_bytes(instance->rx_buffer),
                    ndef_len);
                error = Type4TagErrorWrongFormat;
                break;
            }
            memcpy(&ndef_data[ndef_pos], bit_buffer_get_data(instance->rx_buffer), chunk_len);

            ndef_pos += chunk_len;
            ndef_len -= chunk_len;
        }
        if(error != Type4TagErrorNone) break;

        FURI_LOG_D(
            TAG,
            "Read NDEF file 0x%04X of %lu bytes",
            instance->data->ndef_file_id,
            simple_array_get_count(instance->data->ndef_data));
    } while(false);

    return error;
}
