#include "iso14443_4a_listener_i.h"

#include <nfc/protocols/iso14443_3a/iso14443_3a_listener_i.h>

Iso14443_4aError
    iso14443_4a_listener_send_ats(Iso14443_4aListener* instance, const Iso14443_4aAtsData* data) {
    bit_buffer_reset(instance->tx_buffer);
    bit_buffer_append_byte(instance->tx_buffer, data->tl);

    if(data->tl > 1) {
        bit_buffer_append_byte(instance->tx_buffer, data->t0);
        if(data->t0 & ISO14443_4A_ATS_T0_TA1) {
            bit_buffer_append_byte(instance->tx_buffer, data->ta_1);
        }
        if(data->t0 & ISO14443_4A_ATS_T0_TB1) {
            bit_buffer_append_byte(instance->tx_buffer, data->tb_1);
        }
        if(data->t0 & ISO14443_4A_ATS_T0_TC1) {
            bit_buffer_append_byte(instance->tx_buffer, data->tc_1);
        }

        const uint32_t t1_tk_size = simple_array_get_count(data->t1_tk);
        if(t1_tk_size != 0) {
            bit_buffer_append_bytes(
                instance->tx_buffer, simple_array_cget_data(data->t1_tk), t1_tk_size);
        }
    }

    const Iso14443_3aError error = iso14443_3a_listener_send_standard_frame(
        instance->iso14443_3a_listener, instance->tx_buffer);
    return iso14443_4a_process_error(error);
}

Iso14443_4aError
    iso14443_4a_listener_send_block(Iso14443_4aListener* instance, const BitBuffer* tx_buffer) {
    bit_buffer_reset(instance->tx_buffer);

    // TODO: This is a rudimentary PCB implementation!
    // Just sends back same PCB that was last received from reader,
    // there is no handling of S, R, I blocks and their different flags.
    // We have iso14443_4_layer helper but it is entirely designed for poller,
    // will need large rework for listener, for now this works.
    bit_buffer_append_byte(instance->tx_buffer, instance->pcb_prev);
    bit_buffer_append(instance->tx_buffer, tx_buffer);

    const Iso14443_3aError error = iso14443_3a_listener_send_standard_frame(
        instance->iso14443_3a_listener, instance->tx_buffer);
    return iso14443_4a_process_error(error);
}
