#pragma once

#include "nfc_protocol_formatter_base.h"

#ifdef __cplusplus
extern "C" {
#endif

const NfcProtocolFormatterBase* nfc_protocol_formatter_get(NfcProtocol protocol, NfcMode mode);

#ifdef __cplusplus
}
#endif
