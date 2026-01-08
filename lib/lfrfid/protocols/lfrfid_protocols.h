#pragma once
#include <protocols/protocol.h>
#include "../tools/t5577.h"
#include "../tools/em4305.h"

typedef enum {
    LFRFIDFeatureASK = 1 << 0, /** ASK Demodulation */
    LFRFIDFeaturePSK = 1 << 1, /** PSK Demodulation */
    LFRFIDFeatureRTF = 1 << 2, /** Reader Talks First: ASK Demodulation with 2 way communication */
} LFRFIDFeature;

typedef enum {
    LFRFIDProtocolEM4100,
    LFRFIDProtocolH10301,
    LFRFIDProtocolIdteck,
    LFRFIDProtocolIndala26,
    LFRFIDProtocolIndala224,
    LFRFIDProtocolIOProxXSF,
    LFRFIDProtocolAwid,
    LFRFIDProtocolFDXA,
    LFRFIDProtocolFDXB,
    LFRFIDProtocolHidGeneric,
    LFRFIDProtocolHidExGeneric,
    LFRFIDProtocolPyramid,
    LFRFIDProtocolViking,
    LFRFIDProtocolJablotron,
    LFRFIDProtocolParadox,
    LFRFIDProtocolPACStanley,
    LFRFIDProtocolKeri,
    LFRFIDProtocolGallagher,
    LFRFIDProtocolHitag1,
    LFRFIDProtocolNexwatch,
    LFRFIDProtocolMax,
} LFRFIDProtocol;

extern const ProtocolBase* lfrfid_protocols[];

typedef enum {
    LFRFIDWriteTypeT5577,
    LFRFIDWriteTypeEM4305,
} LFRFIDWriteType;

typedef struct {
    LFRFIDWriteType write_type;
    union {
        LFRFIDT5577 t5577;
        LFRFIDEM4305 em4305;
    };
} LFRFIDWriteRequest;