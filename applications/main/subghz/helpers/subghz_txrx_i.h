#pragma once

#include "subghz_txrx.h"

struct SubGhzTxRx {
    SubGhzWorker* worker;

    SubGhzEnvironment* environment;
    SubGhzReceiver* receiver;
    SubGhzTransmitter* transmitter;
    SubGhzProtocolDecoderBase* decoder_result;
    FlipperFormat* fff_data;

    SubGhzRadioPreset* preset;
    SubGhzSetting* setting;

    uint8_t hopper_timeout;
    uint8_t hopper_idx_frequency;
    bool is_database_loaded;
    SubGhzHopperState hopper_state;

    SubGhzTxRxState txrx_state;
    SubGhzSpeakerState speaker_state;
    const SubGhzDevice* radio_device;
    SubGhzRadioDeviceType radio_device_type;
    //An external module was asked for and answered; radio_device_type is what is
    //actually driving right now, and the two part company when one is unplugged
    bool radio_device_external_wanted;
    //When the last search for a missing module ran, see the probe period
    uint32_t radio_device_probe_tick;

    SubGhzTxRxNeedSaveCallback need_save_callback;
    void* need_save_context;

    bool debug_pin_state;
};
