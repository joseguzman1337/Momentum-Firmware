#include "ntag4xx_poller_i.h"

#include <furi.h>

#include "ntag4xx_i.h"

#define TAG "Ntag4xxPoller"

Ntag4xxError ntag4xx_poller_send_chunks(
    Ntag4xxPoller* instance,
    const BitBuffer* tx_buffer,
    BitBuffer* rx_buffer) {
    furi_check(instance);
    furi_check(instance->iso14443_4a_poller);
    furi_check(instance->tx_buffer);
    furi_check(instance->rx_buffer);
    furi_check(tx_buffer);
    furi_check(rx_buffer);

    Ntag4xxError error = Ntag4xxErrorNone;
    uint8_t status_code = NTAG4XX_STATUS_OPERATION_OK;

    do {
        bit_buffer_reset(instance->tx_buffer);
        bit_buffer_append_byte(instance->tx_buffer, NTAG4XX_CMD_ISO_CLA);
        bit_buffer_append_byte(instance->tx_buffer, bit_buffer_get_byte(tx_buffer, 0));
        bit_buffer_append_byte(instance->tx_buffer, NTAG4XX_CMD_ISO_P1);
        bit_buffer_append_byte(instance->tx_buffer, NTAG4XX_CMD_ISO_P2);
        if(bit_buffer_get_size_bytes(tx_buffer) > 1) {
            bit_buffer_append_byte(instance->tx_buffer, bit_buffer_get_size_bytes(tx_buffer) - 1);
            bit_buffer_append_right(instance->tx_buffer, tx_buffer, 1);
        }
        bit_buffer_append_byte(instance->tx_buffer, NTAG4XX_CMD_ISO_LE);

        Iso14443_4aError iso14443_4a_error = iso14443_4a_poller_send_block(
            instance->iso14443_4a_poller, instance->tx_buffer, instance->rx_buffer);

        if(iso14443_4a_error != Iso14443_4aErrorNone) {
            error = ntag4xx_process_error(iso14443_4a_error);
            break;
        }

        bit_buffer_reset(instance->tx_buffer);
        bit_buffer_append_byte(instance->tx_buffer, NTAG4XX_CMD_ISO_CLA);
        bit_buffer_append_byte(instance->tx_buffer, NTAG4XX_STATUS_ADDITIONAL_FRAME);
        bit_buffer_append_byte(instance->tx_buffer, NTAG4XX_CMD_ISO_P1);
        bit_buffer_append_byte(instance->tx_buffer, NTAG4XX_CMD_ISO_P2);
        bit_buffer_append_byte(instance->tx_buffer, NTAG4XX_CMD_ISO_LE);

        size_t response_len = bit_buffer_get_size_bytes(instance->rx_buffer);
        status_code = NTAG4XX_STATUS_LENGTH_ERROR;
        bit_buffer_reset(rx_buffer);
        if(response_len >= 2 * sizeof(uint8_t) &&
           bit_buffer_get_byte(instance->rx_buffer, response_len - 2) == NTAG4XX_STATUS_ISO_SW1) {
            status_code = bit_buffer_get_byte(instance->rx_buffer, response_len - 1);
            if(response_len > 2 * sizeof(uint8_t)) {
                bit_buffer_copy_left(
                    rx_buffer, instance->rx_buffer, response_len - 2 * sizeof(uint8_t));
            }
        }

        while(status_code == NTAG4XX_STATUS_ADDITIONAL_FRAME) {
            Iso14443_4aError iso14443_4a_error = iso14443_4a_poller_send_block(
                instance->iso14443_4a_poller, instance->tx_buffer, instance->rx_buffer);

            if(iso14443_4a_error != Iso14443_4aErrorNone) {
                error = ntag4xx_process_error(iso14443_4a_error);
                break;
            }

            const size_t rx_size = bit_buffer_get_size_bytes(instance->rx_buffer);
            const size_t rx_capacity_remaining =
                bit_buffer_get_capacity_bytes(rx_buffer) - bit_buffer_get_size_bytes(rx_buffer);

            status_code = rx_size < 2 ? NTAG4XX_STATUS_LENGTH_ERROR :
                                        bit_buffer_get_byte(instance->rx_buffer, rx_size - 1);
            if(rx_size <= rx_capacity_remaining + 2) {
                bit_buffer_set_size_bytes(instance->rx_buffer, rx_size - 2);
                bit_buffer_append(rx_buffer, instance->rx_buffer);
            } else {
                FURI_LOG_W(TAG, "RX buffer overflow: ignoring %zu bytes", rx_size - 2);
            }
        }
    } while(false);

    if(error == Ntag4xxErrorNone) {
        error = ntag4xx_process_status_code(status_code);
    }

    return error;
}

Ntag4xxError ntag4xx_poller_read_version(Ntag4xxPoller* instance, Ntag4xxVersion* data) {
    furi_check(instance);

    bit_buffer_reset(instance->input_buffer);
    bit_buffer_append_byte(instance->input_buffer, NTAG4XX_CMD_GET_VERSION);

    Ntag4xxError error;

    do {
        error =
            ntag4xx_poller_send_chunks(instance, instance->input_buffer, instance->result_buffer);

        if(error != Ntag4xxErrorNone) break;

        if(!ntag4xx_version_parse(data, instance->result_buffer)) {
            error = Ntag4xxErrorProtocol;
        }
    } while(false);

    return error;
}
