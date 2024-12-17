
#pragma once

#include <furi.h>

#ifdef __cplusplus
extern "C" {
#endif

typedef struct {
    uint32_t time;
    uint32_t flags; ///TODO: add nfcPacketType here
    size_t data_size;
    uint8_t* data;
} NfcPacket;

#ifdef __cplusplus
}
#endif
