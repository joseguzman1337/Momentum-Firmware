#pragma once

#include <nfc_mode.h>
#include <nfc/protocols/nfc_protocol.h>

#include <furi.h>

#ifdef __cplusplus
extern "C" {
#endif

typedef uint32_t NfcLoggerFlags;

typedef struct {
    NfcProtocol protocol;
    NfcLoggerFlags request_flags;
    NfcLoggerFlags response_flags;
} FURI_PACKED NfcLoggerHistory;

#define NFC_LOG_FLAG(flag_register, flag)    (flag_register |= flag)
#define NFC_LOG_FLAG_REQUEST(history, flag)  (NFC_LOG_FLAG(history.request_flags, flag))
#define NFC_LOG_FLAG_RESPONSE(history, flag) (NFC_LOG_FLAG(history.response_flags, flag))

#define NFC_LOG_FLAG_FLUSH(history) \
    do {                            \
        history.request_flags = 0;  \
        history.response_flags = 0; \
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

#ifdef __cplusplus
}
#endif
