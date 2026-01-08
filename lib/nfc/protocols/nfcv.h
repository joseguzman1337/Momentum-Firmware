#pragma once

#include <stdbool.h>
#include <stdint.h>

typedef struct FuriHalNfcDevData FuriHalNfcDevData;
typedef struct FuriHalNfcTxRxContext FuriHalNfcTxRxContext;

typedef int32_t ReturnCode;

#ifdef __cplusplus
extern "C" {
#endif

#define NFCV_UID_LENGTH       (8U)
#define NFCV_COMMAND_RETRIES  (3U)
#define NFCV_FRAMESIZE_MAX    (256U)
#define NFCV_PULSE_BUFFER     (512U)
#define NFCV_PULSE_DURATION_NS (2360U)
#define NFCV_LAST_COMMAND_SIZE (128U)
#define NFCV_SUB_DATA_SIZE     (64U)
#define NFCV_DIAGNOSTIC_DUMP_SIZE (128U)

#define NFCV_FC_HZ (13560000U)

/* modulation polarity for load modulation */
#define NFCV_LOAD_MODULATION_POLARITY (true)

/* NFC-V response timing in seconds */
#define NFCV_RESP_SUBC1_UNMOD_256 (256.0f / (float)NFCV_FC_HZ)
#define NFCV_RESP_SUBC1_PULSE_32  (32.0f / (float)NFCV_FC_HZ)

typedef enum {
    NFCV_SIG_SOF,
    NFCV_SIG_BIT0,
    NFCV_SIG_BIT1,
    NFCV_SIG_EOF,
    NFCV_SIG_LOW_SOF,
    NFCV_SIG_LOW_BIT0,
    NFCV_SIG_LOW_BIT1,
    NFCV_SIG_LOW_EOF,
} NfcVSignalIndex;

typedef enum {
    NFCV_FRAME_STATE_SOF1,
    NFCV_FRAME_STATE_SOF2,
    NFCV_FRAME_STATE_CODING_256,
    NFCV_FRAME_STATE_CODING_4,
    NFCV_FRAME_STATE_EOF,
    NFCV_FRAME_STATE_RESET,
} NfcVFrameState;

typedef enum {
    NfcVSendFlagsNormal = 0,
    NfcVSendFlagsSof = (1U << 0),
    NfcVSendFlagsCrc = (1U << 1),
    NfcVSendFlagsEof = (1U << 2),
    NfcVSendFlagsOneSubcarrier = (1U << 3),
    NfcVSendFlagsTwoSubcarrier = (1U << 4),
    NfcVSendFlagsHighRate = (1U << 5),
} NfcVSendFlags;

typedef enum {
    NfcVTypePlain,
    NfcVTypeSlix,
    NfcVTypeSlix2,
    NfcVTypeSlixS,
    NfcVTypeSlixL,
    NfcVTypeSniff,
} NfcVType;

typedef enum {
    NfcVLockBitDsfid = (1U << 1),
    NfcVLockBitAfi = (1U << 2),
} NfcVLockBit;

/* Request flags */
#define NFCV_REQ_FLAG_SUB_CARRIER (1U << 0)
#define NFCV_REQ_FLAG_DATA_RATE   (1U << 1)
#define NFCV_REQ_FLAG_INVENTORY   (1U << 2)
#define NFCV_REQ_FLAG_SELECT      (1U << 4)
#define NFCV_REQ_FLAG_ADDRESS     (1U << 5)
#define NFCV_REQ_FLAG_OPTION      (1U << 6)
#define NFCV_REQ_FLAG_AFI         (1U << 4)

/* Response flags and errors */
#define NFCV_RES_FLAG_ERROR (1U << 0)
#define NFCV_NOERROR        (0x00U)
#define NFCV_ERROR_GENERIC  (0x0FU)

/* System info flags */
#define NFCV_SYSINFO_FLAG_DSFID   (1U << 0)
#define NFCV_SYSINFO_FLAG_AFI     (1U << 1)
#define NFCV_SYSINFO_FLAG_MEMSIZE (1U << 2)
#define NFCV_SYSINFO_FLAG_ICREF   (1U << 3)

/* Commands */
#define NFCV_CMD_INVENTORY        (0x01U)
#define NFCV_CMD_STAY_QUIET       (0x02U)
#define NFCV_CMD_READ_BLOCK       (0x20U)
#define NFCV_CMD_WRITE_BLOCK      (0x21U)
#define NFCV_CMD_LOCK_BLOCK       (0x22U)
#define NFCV_CMD_READ_MULTI_BLOCK (0x23U)
#define NFCV_CMD_WRITE_MULTI_BLOCK (0x24U)
#define NFCV_CMD_SELECT           (0x25U)
#define NFCV_CMD_RESET_TO_READY   (0x26U)
#define NFCV_CMD_WRITE_AFI        (0x27U)
#define NFCV_CMD_LOCK_AFI         (0x28U)
#define NFCV_CMD_WRITE_DSFID      (0x29U)
#define NFCV_CMD_LOCK_DSFID       (0x2AU)
#define NFCV_CMD_GET_SYSTEM_INFO  (0x2BU)
#define NFCV_CMD_ADVANCED         (0xA0U)
#define NFCV_CMD_CUST_ECHO_MODE   (0xA0U)
#define NFCV_CMD_CUST_ECHO_DATA   (0xA1U)

typedef struct DigitalSignal DigitalSignal;
typedef struct DigitalSequence DigitalSequence;
typedef struct PulseReader PulseReader;
typedef struct NfcVData NfcVData;
typedef struct NfcVReader NfcVReader;

typedef struct {
    DigitalSignal* nfcv_resp_one;
    DigitalSignal* nfcv_resp_zero;
    DigitalSignal* nfcv_resp_sof;
    DigitalSignal* nfcv_resp_eof;
} NfcVEmuAirSignals;

typedef struct {
    DigitalSequence* nfcv_signal;
    DigitalSignal* nfcv_resp_unmod;
    DigitalSignal* nfcv_resp_pulse;
    DigitalSignal* nfcv_resp_half_pulse;
    PulseReader* reader_signal;
    NfcVEmuAirSignals signals_high;
    NfcVEmuAirSignals signals_low;
} NfcVEmuAir;

typedef bool (*NfcVEmuProtocolFilter)(
    FuriHalNfcTxRxContext* tx_rx,
    FuriHalNfcDevData* nfc_data,
    NfcVData* nfcv_data);

typedef void (*NfcVEmuProtocolHandler)(
    FuriHalNfcTxRxContext* tx_rx,
    FuriHalNfcDevData* nfc_data,
    void* nfcv_data_in);

typedef struct {
    uint8_t flags;
    uint8_t command;
    bool selected;
    bool addressed;
    bool advanced;
    uint8_t address_offset;
    uint8_t payload_offset;
    NfcVSendFlags response_flags;
    uint32_t send_time;
    uint8_t response_buffer[NFCV_FRAMESIZE_MAX];
    NfcVEmuProtocolFilter emu_protocol_filter;
} NfcVEmuProtocolCtx;

typedef struct {
    uint8_t data[NFCV_SUB_DATA_SIZE];
} NfcVSubData;

struct NfcVData {
    uint8_t dsfid;
    uint8_t afi;
    uint8_t ic_ref;
    uint16_t block_num;
    uint8_t block_size;

    uint8_t* data;
    uint8_t* security_status;

    bool ready;
    bool quiet;
    bool selected;
    bool modified;
    bool echo_mode;

    NfcVType sub_type;
    NfcVSubData sub_data;

    char last_command[NFCV_LAST_COMMAND_SIZE];

    uint8_t* frame;
    uint32_t frame_length;
    uint32_t eof_timestamp;

    NfcVEmuAir emu_air;
    NfcVEmuProtocolCtx* emu_protocol_ctx;
    NfcVEmuProtocolHandler emu_protocol_handler;
};

ReturnCode nfcv_inventory(uint8_t* uid);
ReturnCode nfcv_read_blocks(NfcVReader* reader, NfcVData* nfcv_data);
ReturnCode nfcv_read_sysinfo(FuriHalNfcDevData* nfc_data, NfcVData* nfcv_data);
bool nfcv_read_card(NfcVReader* reader, FuriHalNfcDevData* nfc_data, NfcVData* nfcv_data);

void nfcv_emu_init(FuriHalNfcDevData* nfc_data, NfcVData* nfcv_data);
void nfcv_emu_deinit(NfcVData* nfcv_data);
bool nfcv_emu_loop(
    FuriHalNfcTxRxContext* tx_rx,
    FuriHalNfcDevData* nfc_data,
    NfcVData* nfcv_data,
    uint32_t timeout_ms);

#ifdef __cplusplus
}
#endif
