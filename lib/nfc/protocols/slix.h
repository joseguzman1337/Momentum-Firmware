#pragma once

#include <stdbool.h>

#include "nfcv.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef struct NfcVData NfcVData;

bool slix_check_card_type(FuriHalNfcDevData* nfc_data);
bool slix2_check_card_type(FuriHalNfcDevData* nfc_data);
bool slix_s_check_card_type(FuriHalNfcDevData* nfc_data);
bool slix_l_check_card_type(FuriHalNfcDevData* nfc_data);

ReturnCode slix2_read_custom(FuriHalNfcDevData* nfc_data, NfcVData* nfcv_data);

void slix_prepare(NfcVData* nfcv_data);
void slix2_prepare(NfcVData* nfcv_data);
void slix_s_prepare(NfcVData* nfcv_data);
void slix_l_prepare(NfcVData* nfcv_data);

#ifdef __cplusplus
}
#endif
