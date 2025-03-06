#include "type_4_tag_i.h"

#define TAG "Type4Tag"

#define TYPE_4_TAG_FFF_NDEF_DATA_SIZE_KEY "NDEF Data Size"
#define TYPE_4_TAG_FFF_NDEF_DATA_KEY      "NDEF Data"

#define TYPE_4_TAG_FFF_NDEF_DATA_PER_LINE (16U)

bool type_4_tag_ndef_data_load(Type4TagData* data, FlipperFormat* ff) {
    uint32_t ndef_data_size;
    if(!flipper_format_read_uint32(ff, TYPE_4_TAG_FFF_NDEF_DATA_SIZE_KEY, &ndef_data_size, 1)) {
        return false;
    }
    if(ndef_data_size == 0) {
        return true;
    }

    simple_array_init(data->ndef_data, ndef_data_size);

    uint32_t ndef_data_pos = 0;
    uint8_t* ndef_data = simple_array_get_data(data->ndef_data);
    while(ndef_data_size > 0) {
        uint8_t ndef_line_size = MIN(ndef_data_size, TYPE_4_TAG_FFF_NDEF_DATA_PER_LINE);

        if(!flipper_format_read_hex(
               ff, TYPE_4_TAG_FFF_NDEF_DATA_KEY, &ndef_data[ndef_data_pos], ndef_line_size)) {
            simple_array_reset(data->ndef_data);
            return false;
        }

        ndef_data_pos += ndef_line_size;
        ndef_data_size -= ndef_line_size;
    }

    return true;
}

bool type_4_tag_ndef_data_save(const Type4TagData* data, FlipperFormat* ff) {
    uint32_t ndef_data_size = simple_array_get_count(data->ndef_data);
    if(!flipper_format_write_uint32(ff, TYPE_4_TAG_FFF_NDEF_DATA_SIZE_KEY, &ndef_data_size, 1)) {
        return false;
    }
    if(ndef_data_size == 0) {
        return true;
    }

    uint32_t ndef_data_pos = 0;
    uint8_t* ndef_data = simple_array_get_data(data->ndef_data);
    while(ndef_data_size > 0) {
        uint8_t ndef_line_size = MIN(ndef_data_size, TYPE_4_TAG_FFF_NDEF_DATA_PER_LINE);

        if(!flipper_format_write_hex(
               ff, TYPE_4_TAG_FFF_NDEF_DATA_KEY, &ndef_data[ndef_data_pos], ndef_line_size)) {
            return false;
        }

        ndef_data_pos += ndef_line_size;
        ndef_data_size -= ndef_line_size;
    }

    return true;
}
