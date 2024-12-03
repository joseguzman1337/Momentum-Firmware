#pragma once

//#include <nfc/nfc.h>
#include <nfc_mode.h>
#include <nfc/protocols/nfc_protocol.h>

/*
#include <nfc/protocols/mf_ultralight/mf_ultralight_poller_i.h>
#include <nfc/protocols/mf_ultralight/mf_ultralight_listener.h> */

#include <furi.h>

#ifdef __cplusplus
extern "C" {
#endif

typedef uint32_t NfcLoggerFlags;

#define NFC_LOG_FLAG_GET(flag_register, flag) ((flag_register & flag) == flag)
#define NFC_LOG_FLAG_SET(flag_register, flag) (flag_register |= flag)
#define NFC_LOG_FLAG_REQUEST(history, flag)   (NFC_LOG_FLAG_SET(history.request_flags, flag))
#define NFC_LOG_FLAG_RESPONSE(history, flag)  (NFC_LOG_FLAG_SET(history.response_flags, flag))

#define NFC_LOG_FLAG_FLUSH(history) \
    do {                            \
        history.request_flags = 0;  \
    } while(false);

///TODO:rename to NFC_FLAG_HAL
#define NFC_FLAG_USER_ABORT         (1 << 0)
#define NFC_FLAG_FIELD_ON           (1 << 1)
#define NFC_FLAG_FIELD_OFF          (1 << 2)
#define NFC_FLAG_LISTENER_ACTIVATED (1 << 3)
#define NFC_FLAG_RX_END             (1 << 4)

#define NFC_FLAG_ISO14443_3A_CRC_OK    (1 << 0)
#define NFC_FLAG_ISO14443_3A_CRC_BAD   (1 << 1)
#define NFC_FLAG_ISO14443_3A_ACTIVATED (1 << 2)
#define NFC_FLAG_ISO14443_3A_HALT      (1 << 3)
#define NFC_FLAG_ISO14443_3A_FIELD_OFF (1 << 4)
#define NFC_FLAG_ISO14443_3A_ERROR     (1 << 5)

#define NFC_FLAG_MF_ULTRALIGHT_CMD                       (1 << 0)
#define NFC_FLAG_MF_ULTRALIGHT_COMPOSITE_CMD_IN_PROGRESS (1 << 1)
#define NFC_FLAG_MF_ULTRALIGHT_RESET_STATE               (1 << 2)

//---------------------------------------------------
/* typedef union {
    MfUltralightPollerEventType poller_event;
    MfUltralightListenerEventType listener_event;
} NfcHistoryEventType_MfUltralight;

typedef union {
    MfUltralightPollerState poller_state;
} NfcHistoryState_MfUltralight;

typedef struct {
    NfcHistoryEventType_MfUltralight event;
    NfcHistoryState_MfUltralight state;
    NfcCommand command;
} FURI_PACKED NfcHistoryData_MfUltralight; */

void nfc_logger_flag_parse(NfcProtocol protocol, uint32_t flags, FuriString* output);
#ifdef __cplusplus
}
#endif
