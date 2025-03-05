#pragma once

#include "type_4_tag.h"

#define TYPE_4_TAG_ISO_SELECT_CMD        0x00, 0xA4
#define TYPE_4_TAG_ISO_SELECT_P1_BY_NAME (0x04)
#define TYPE_4_TAG_ISO_SELECT_P1_BY_ID   (0x00)
#define TYPE_4_TAG_ISO_SELECT_P2_EMPTY   (0x0C)
#define TYPE_4_TAG_ISO_SELECT_LE_EMPTY   (0x00)

#define TYPE_4_TAG_ISO_READ_CMD          0x00, 0xB0
#define TYPE_4_TAG_ISO_READ_P1_EMPTY     (0x00)
#define TYPE_4_TAG_ISO_READ_P2_BEGINNING (0x00)
#define TYPE_4_TAG_ISO_READ_LE_FULL      (0x00)

#define TYPE_4_TAG_ISO_STATUS_LEN     (2)
#define TYPE_4_TAG_ISO_STATUS_SUCCESS 0x90, 0x00
#define TYPE_4_TAG_ISO_RW_CHUNK_LEN   (255)
#define TYPE_4_TAG_ISO_APP_NAME_LEN   (7)
#define TYPE_4_TAG_ISO_APP_NAME       0xD2, 0x76, 0x00, 0x00, 0x85, 0x01, 0x01
#define TYPE_4_TAG_T4T_CC_FILE_ID_LEN (2)
#define TYPE_4_TAG_T4T_CC_FILE_ID     0xE1, 0x03

#define TYPE_4_TAG_T4T_CC_VNO 0x20

typedef enum FURI_PACKED {
    Type4TagCcTlvTypeNdefFileCtrl = 0x04,
    Type4TagCcTlvTypeProprietaryFileCtrl = 0x05,
} Type4TagCcTlvType;

typedef struct FURI_PACKED {
    uint16_t file_id;
    uint16_t max_len;
    uint8_t read_perm;
    uint8_t write_perm;
} Type4TagCcTlvNdefFileCtrl;

typedef union FURI_PACKED {
    Type4TagCcTlvNdefFileCtrl ndef_file_ctrl;
} Type4TagCcTlvValue;

typedef struct FURI_PACKED {
    Type4TagCcTlvType type;
    uint8_t len;
    Type4TagCcTlvValue value;
} Type4TagCcTlv;

typedef struct FURI_PACKED {
    uint16_t len;
    uint8_t t4t_vno;
    uint16_t mle;
    uint16_t mlc;
    Type4TagCcTlv tlv[];
} Type4TagCc;
