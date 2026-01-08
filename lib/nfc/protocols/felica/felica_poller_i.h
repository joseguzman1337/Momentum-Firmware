#pragma once

#include "felica_poller.h"
#include "felica_poller_history_data.h"
#include <toolbox/bit_buffer.h>
#include <helpers/logger/nfc_logger_i.h>

#ifdef __cplusplus
extern "C" {
#endif

#define FELICA_POLLER_MAX_BUFFER_SIZE (256U)

#define FELICA_POLLER_POLLING_FWT (200000U)

#define FELICA_POLLER_CMD_POLLING_REQ_CODE  (0x00U)
#define FELICA_POLLER_CMD_POLLING_RESP_CODE (0x01U)

struct FelicaPoller {
    Nfc* nfc;
    FelicaPollerState state;
    FelicaAuthentication auth;

    FelicaData* data;
    BitBuffer* tx_buffer;
    BitBuffer* rx_buffer;

    NfcGenericEvent general_event;
    FelicaPollerEvent felica_event;
    FelicaPollerEventData felica_event_data;
    NfcGenericCallback callback;
    NfcGenericLogHistoryCallback log_callback;
    uint8_t block_index;
    uint8_t systems_read;
    uint8_t systems_total;
    NfcHistoryItem history;
    FelicaPollerHistoryData history_data;
    void* context;
};

typedef struct {
    uint16_t system_code;
    uint8_t request_code;
    uint8_t time_slot;
} FelicaPollerPollingCommand;

typedef struct {
    FelicaIDm idm;
    FelicaPMm pmm;
    uint8_t request_data[2];
} FelicaPollerPollingResponse;

const FelicaData* felica_poller_get_data(FelicaPoller* instance);

/**
 * @brief Performs felica polling operation as part of the activation process
 * 
 * @param[in, out] instance pointer to the instance to be used in the transaction.
 * @param[in] cmd Pointer to polling command structure
 * @param[out] resp Pointer to the response structure
 * @return FelicaErrorNone on success, an error code on failure
*/
FelicaError felica_poller_polling(
    FelicaPoller* instance,
    const FelicaPollerPollingCommand* cmd,
    FelicaPollerPollingResponse* resp);

/**
 * @brief Performs felica write operation with data provided as parameters
 * 
 * @param[in, out] instance pointer to the instance to be used in the transaction.
 * @param[in] block_count Amount of blocks involved in writing procedure
 * @param[in] block_numbers Array with block indexes according to felica docs
 * @param[in] data Data of blocks provided in block_numbers
 * @param[out] response_ptr Pointer to the response structure
 * @return FelicaErrorNone on success, an error code on failure.
*/
FelicaError felica_poller_write_blocks(
    FelicaPoller* instance,
    const uint8_t block_count,
    const uint8_t* const block_numbers,
    const uint8_t* data,
    FelicaPollerWriteCommandResponse** const response_ptr);

FelicaError felica_poller_read_blocks(
    FelicaPoller* instance,
    uint8_t block_count,
    const uint8_t* block_list,
    uint16_t service_code,
    FelicaPollerReadCommandResponse** response);

FelicaError felica_poller_list_service_by_cursor(
    FelicaPoller* instance,
    uint16_t cursor,
    FelicaListServiceCommandResponse** response);

FelicaError felica_poller_list_system_code(
    FelicaPoller* instance,
    FelicaListSystemCodeCommandResponse** response);

#ifdef __cplusplus
}
#endif
