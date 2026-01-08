#include "slix.h"

#include <furi.h>

bool slix_check_card_type(FuriHalNfcDevData* nfc_data) {
    UNUSED(nfc_data);
    return false;
}

bool slix2_check_card_type(FuriHalNfcDevData* nfc_data) {
    UNUSED(nfc_data);
    return false;
}

bool slix_s_check_card_type(FuriHalNfcDevData* nfc_data) {
    UNUSED(nfc_data);
    return false;
}

bool slix_l_check_card_type(FuriHalNfcDevData* nfc_data) {
    UNUSED(nfc_data);
    return false;
}

ReturnCode slix2_read_custom(FuriHalNfcDevData* nfc_data, NfcVData* nfcv_data) {
    UNUSED(nfc_data);
    UNUSED(nfcv_data);
    return ERR_NONE;
}

void slix_prepare(NfcVData* nfcv_data) {
    UNUSED(nfcv_data);
}

void slix2_prepare(NfcVData* nfcv_data) {
    UNUSED(nfcv_data);
}

void slix_s_prepare(NfcVData* nfcv_data) {
    UNUSED(nfcv_data);
}

void slix_l_prepare(NfcVData* nfcv_data) {
    UNUSED(nfcv_data);
}
