#include "type_4_tag_listener_i.h"
#include "type_4_tag_i.h"

#include <bit_lib/bit_lib.h>

#define TAG "Type4TagListener"

typedef Type4TagError (*Type4TagListenerApduHandler)(
    Type4TagListener* instance,
    uint8_t p1,
    uint8_t p2,
    size_t lc,
    const uint8_t* data,
    size_t le);

typedef struct {
    uint8_t cla_ins[2];
    Type4TagListenerApduHandler handler;
} Type4TagListenerApduCommand;

static const uint8_t type_4_tag_success_apdu[] = {TYPE_4_TAG_ISO_STATUS_SUCCESS};
static const uint8_t type_4_tag_offset_error_apdu[] = {TYPE_4_TAG_ISO_STATUS_OFFSET_ERR};
static const uint8_t type_4_tag_not_found_apdu[] = {TYPE_4_TAG_ISO_STATUS_NOT_FOUND};
static const uint8_t type_4_tag_no_support_apdu[] = {TYPE_4_TAG_ISO_STATUS_NO_SUPPORT};
static const uint8_t type_4_tag_bad_params_apdu[] = {TYPE_4_TAG_ISO_STATUS_BAD_PARAMS};
static const uint8_t type_4_tag_no_cmd_apdu[] = {TYPE_4_TAG_ISO_STATUS_NO_CMD};

static Type4TagError type_4_tag_listener_iso_select(
    Type4TagListener* instance,
    uint8_t p1,
    uint8_t p2,
    size_t lc,
    const uint8_t* data,
    size_t le) {
    UNUSED(p2);
    UNUSED(le);

    if(p1 == TYPE_4_TAG_ISO_SELECT_P1_BY_DF_NAME) {
        static const uint8_t t4t_app[TYPE_4_TAG_ISO_APP_NAME_LEN] = {TYPE_4_TAG_ISO_APP_NAME};
        if(lc == sizeof(t4t_app) && memcmp(t4t_app, data, sizeof(t4t_app)) == 0) {
            instance->state = Type4TagListenerStateSelectedApplication;
            bit_buffer_append_bytes(
                instance->tx_buffer, type_4_tag_success_apdu, sizeof(type_4_tag_success_apdu));
            return Type4TagErrorNone;
        }

        instance->state = Type4TagListenerStateIdle;
        bit_buffer_append_bytes(
            instance->tx_buffer, type_4_tag_not_found_apdu, sizeof(type_4_tag_not_found_apdu));
        return Type4TagErrorCustomCommand;
    }

    if(instance->state >= Type4TagListenerStateSelectedApplication) {
        if(p1 == TYPE_4_TAG_ISO_SELECT_P1_BY_ID || p1 == TYPE_4_TAG_ISO_SELECT_P1_BY_EF_ID) {
            static const uint8_t cc_id[TYPE_4_TAG_T4T_CC_FILE_ID_LEN] = {
                TYPE_4_TAG_T4T_CC_FILE_ID};
            if(lc == sizeof(cc_id) && memcmp(cc_id, data, sizeof(cc_id)) == 0) {
                instance->state = Type4TagListenerStateSelectedCapabilityContainer;
                bit_buffer_append_bytes(
                    instance->tx_buffer, type_4_tag_success_apdu, sizeof(type_4_tag_success_apdu));
                return Type4TagErrorNone;
            }

            uint8_t ndef_file_id_be[sizeof(instance->data->ndef_file_id)];
            bit_lib_num_to_bytes_be(
                instance->data->is_tag_specific ? instance->data->ndef_file_id :
                                                  TYPE_4_TAG_T4T_DEFAULT_FILE_ID,
                sizeof(ndef_file_id_be),
                ndef_file_id_be);
            if(lc == sizeof(ndef_file_id_be) &&
               memcmp(ndef_file_id_be, data, sizeof(ndef_file_id_be)) == 0) {
                instance->state = Type4TagListenerStateSelectedNdefMessage;
                bit_buffer_append_bytes(
                    instance->tx_buffer, type_4_tag_success_apdu, sizeof(type_4_tag_success_apdu));
                return Type4TagErrorNone;
            }
        }
    }

    instance->state = Type4TagListenerStateIdle;
    bit_buffer_append_bytes(
        instance->tx_buffer, type_4_tag_not_found_apdu, sizeof(type_4_tag_not_found_apdu));
    return Type4TagErrorCustomCommand;
}

static Type4TagError type_4_tag_listener_iso_read(
    Type4TagListener* instance,
    uint8_t p1,
    uint8_t p2,
    size_t lc,
    const uint8_t* data,
    size_t le) {
    UNUSED(lc);
    UNUSED(data);

    size_t offset;
    if(p1 & TYPE_4_TAG_ISO_READ_P1_ID_MASK) {
        bit_buffer_append_bytes(
            instance->tx_buffer, type_4_tag_no_support_apdu, sizeof(type_4_tag_no_support_apdu));
        return Type4TagErrorCustomCommand;
    } else {
        offset = (p1 << 8) + p2;
    }

    if(instance->state == Type4TagListenerStateSelectedCapabilityContainer) {
        uint8_t cc_buf[sizeof(Type4TagCc) + sizeof(Type4TagCcTlv)];
        if(offset >= sizeof(cc_buf)) {
            bit_buffer_append_bytes(
                instance->tx_buffer,
                type_4_tag_offset_error_apdu,
                sizeof(type_4_tag_offset_error_apdu));
            return Type4TagErrorWrongFormat;
        }
        Type4TagCc* cc = (Type4TagCc*)cc_buf;
        bit_lib_num_to_bytes_be(sizeof(cc_buf), sizeof(cc->len), (void*)&cc->len);
        cc->t4t_vno = TYPE_4_TAG_T4T_CC_VNO;
        bit_lib_num_to_bytes_be(
            instance->data->is_tag_specific ?
                MIN(instance->data->chunk_max_read, TYPE_4_TAG_CHUNK_LEN) :
                TYPE_4_TAG_CHUNK_LEN,
            sizeof(cc->mle),
            (void*)&cc->mle);
        bit_lib_num_to_bytes_be(
            instance->data->is_tag_specific ?
                MIN(instance->data->chunk_max_write, TYPE_4_TAG_CHUNK_LEN) :
                TYPE_4_TAG_CHUNK_LEN,
            sizeof(cc->mlc),
            (void*)&cc->mlc);
        cc->tlv[0].type = Type4TagCcTlvTypeNdefFileCtrl;
        cc->tlv[0].len = sizeof(cc->tlv[0].value.ndef_file_ctrl);
        bit_lib_num_to_bytes_be(
            instance->data->is_tag_specific ? instance->data->ndef_file_id :
                                              TYPE_4_TAG_T4T_DEFAULT_FILE_ID,
            sizeof(cc->tlv[0].value.ndef_file_ctrl.file_id),
            (void*)&cc->tlv[0].value.ndef_file_ctrl.file_id);
        bit_lib_num_to_bytes_be(
            instance->data->is_tag_specific ? instance->data->ndef_max_len :
                                              TYPE_4_TAG_DEFAULT_SIZE,
            sizeof(cc->tlv[0].value.ndef_file_ctrl.max_len),
            (void*)&cc->tlv[0].value.ndef_file_ctrl.max_len);
        cc->tlv[0].value.ndef_file_ctrl.read_perm = instance->data->is_tag_specific ?
                                                        instance->data->ndef_read_lock :
                                                        TYPE_4_TAG_T4T_CC_RW_LOCK_NONE;
        cc->tlv[0].value.ndef_file_ctrl.write_perm = instance->data->is_tag_specific ?
                                                         instance->data->ndef_write_lock :
                                                         TYPE_4_TAG_T4T_CC_RW_LOCK_NONE;

        bit_buffer_append_bytes(
            instance->tx_buffer, cc_buf + offset, MIN(sizeof(cc_buf) - offset, le));
        bit_buffer_append_bytes(
            instance->tx_buffer, type_4_tag_success_apdu, sizeof(type_4_tag_success_apdu));
        return Type4TagErrorNone;
    }

    if(instance->state == Type4TagListenerStateSelectedNdefMessage) {
        size_t ndef_file_len = simple_array_get_count(instance->data->ndef_data);
        bool included_len = false;
        if(offset < sizeof(uint16_t)) {
            uint8_t ndef_file_len_be[sizeof(uint16_t)];
            bit_lib_num_to_bytes_be(ndef_file_len, sizeof(ndef_file_len_be), ndef_file_len_be);
            uint8_t read_len = MIN(sizeof(ndef_file_len_be) - offset, le);
            bit_buffer_append_bytes(instance->tx_buffer, &ndef_file_len_be[offset], read_len);
            included_len = true;
            offset = sizeof(uint16_t);
            le -= read_len;
        }
        offset -= sizeof(uint16_t);

        if(offset >= ndef_file_len) {
            if(included_len) {
                bit_buffer_append_bytes(
                    instance->tx_buffer, type_4_tag_success_apdu, sizeof(type_4_tag_success_apdu));
                return Type4TagErrorNone;
            } else {
                bit_buffer_append_bytes(
                    instance->tx_buffer,
                    type_4_tag_offset_error_apdu,
                    sizeof(type_4_tag_offset_error_apdu));
                return Type4TagErrorWrongFormat;
            }
        }
        const uint8_t* ndef_data = simple_array_cget_data(instance->data->ndef_data);
        bit_buffer_append_bytes(
            instance->tx_buffer, &ndef_data[offset], MIN(ndef_file_len - offset, le));
        bit_buffer_append_bytes(
            instance->tx_buffer, type_4_tag_success_apdu, sizeof(type_4_tag_success_apdu));
        return Type4TagErrorNone;
    }

    bit_buffer_append_bytes(
        instance->tx_buffer, type_4_tag_not_found_apdu, sizeof(type_4_tag_not_found_apdu));
    return Type4TagErrorCustomCommand;
}

static const Type4TagListenerApduCommand type_4_tag_listener_commands[] = {
    {
        .cla_ins = {TYPE_4_TAG_ISO_SELECT_CMD},
        .handler = type_4_tag_listener_iso_select,
    },
    {
        .cla_ins = {TYPE_4_TAG_ISO_READ_CMD},
        .handler = type_4_tag_listener_iso_read,
    },
};

Type4TagError
    type_4_tag_listener_handle_apdu(Type4TagListener* instance, const BitBuffer* rx_buffer) {
    Type4TagError error = Type4TagErrorNone;

    bit_buffer_reset(instance->tx_buffer);

    do {
        typedef struct {
            uint8_t cla_ins[2];
            uint8_t p1;
            uint8_t p2;
            uint8_t body[];
        } Type4TagApdu;

        const size_t buf_size = bit_buffer_get_size_bytes(rx_buffer);

        if(buf_size < sizeof(Type4TagApdu)) {
            error = Type4TagErrorWrongFormat;
            break;
        }

        const Type4TagApdu* apdu = (const Type4TagApdu*)bit_buffer_get_data(rx_buffer);

        Type4TagListenerApduHandler handler = NULL;
        for(size_t i = 0; i < COUNT_OF(type_4_tag_listener_commands); i++) {
            const Type4TagListenerApduCommand* command = &type_4_tag_listener_commands[i];
            if(memcmp(apdu->cla_ins, command->cla_ins, sizeof(apdu->cla_ins)) == 0) {
                handler = command->handler;
                break;
            }
        }
        if(!handler) {
            bit_buffer_append_bytes(
                instance->tx_buffer, type_4_tag_no_cmd_apdu, sizeof(type_4_tag_no_cmd_apdu));
            error = Type4TagErrorCustomCommand;
            break;
        }

        size_t body_size = buf_size - offsetof(Type4TagApdu, body);
        size_t lc;
        const uint8_t* data = apdu->body;
        size_t le;
        if(body_size == 0) {
            lc = 0;
            data = NULL;
            le = 0;
        } else if(body_size == 1) {
            lc = 0;
            data = NULL;
            le = apdu->body[0];
            if(le == 0) {
                le = 256;
            }
        } else if(body_size == 3 && apdu->body[0] == 0) {
            lc = 0;
            data = NULL;
            le = bit_lib_bytes_to_num_be(&apdu->body[1], sizeof(uint16_t));
            if(le == 0) {
                le = 65536;
            }
        } else {
            bool extended_lc = false;
            if(data[0] == 0) {
                extended_lc = true;
                lc = bit_lib_bytes_to_num_be(&data[1], sizeof(uint16_t));
                data += 1 + sizeof(uint16_t);
                body_size -= 1 + sizeof(uint16_t);
            } else {
                lc = data[0];
                data++;
                body_size--;
            }
            if(lc == 0 || body_size < lc) {
                bit_buffer_append_bytes(
                    instance->tx_buffer,
                    type_4_tag_bad_params_apdu,
                    sizeof(type_4_tag_bad_params_apdu));
                error = Type4TagErrorWrongFormat;
                break;
            }

            if(body_size == lc) {
                le = 0;
            } else if(!extended_lc && body_size - lc == 1) {
                le = data[lc];
                if(le == 0) {
                    le = 256;
                }
            } else if(extended_lc && body_size - lc == 2) {
                le = bit_lib_bytes_to_num_be(&data[lc], sizeof(uint16_t));
                if(le == 0) {
                    le = 65536;
                }
            } else {
                bit_buffer_append_bytes(
                    instance->tx_buffer,
                    type_4_tag_bad_params_apdu,
                    sizeof(type_4_tag_bad_params_apdu));
                error = Type4TagErrorWrongFormat;
                break;
            }
        }

        error = handler(instance, apdu->p1, apdu->p2, lc, data, le);
    } while(false);

    if(bit_buffer_get_size_bytes(instance->tx_buffer) > 0) {
        const Iso14443_4aError iso14443_4a_error =
            iso14443_4a_listener_send_block(instance->iso14443_4a_listener, instance->tx_buffer);

        // Keep error flag to show unknown command on screen
        if(error != Type4TagErrorCustomCommand) {
            error = type_4_tag_process_error(iso14443_4a_error);
        }
    }

    return error;
}
