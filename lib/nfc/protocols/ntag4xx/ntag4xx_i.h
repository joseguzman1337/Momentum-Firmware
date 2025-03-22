#pragma once

#include "ntag4xx.h"

#define NTAG4XX_FFF_PICC_PREFIX "PICC"

// ISO 7816 command wrapping
#define NTAG4XX_CMD_ISO_CLA    (0x90)
#define NTAG4XX_CMD_ISO_P1     (0x00)
#define NTAG4XX_CMD_ISO_P2     (0x00)
#define NTAG4XX_CMD_ISO_LE     (0x00)
// ISO 7816 status wrapping
#define NTAG4XX_STATUS_ISO_SW1 (0x91)

// Successful operation
#define NTAG4XX_STATUS_OPERATION_OK         (0x00)
// Command code not supported
#define NTAG4XX_STATUS_ILLEGAL_COMMAND_CODE (0x1C)
// CRC or MAC does not match data Padding bytes not valid
#define NTAG4XX_STATUS_INTEGRITY_ERROR      (0x1E)
// Invalid key number specified
#define NTAG4XX_STATUS_NO_SUCH_KEY          (0x40)
// Length of command string invalid
#define NTAG4XX_STATUS_LENGTH_ERROR         (0x7E)
// Current configuration / status does not allow the requested command
#define NTAG4XX_STATUS_PERMISSION_DENIED    (0x9D)
// Value of the parameter(s) invalid
#define NTAG4XX_STATUS_PARAMETER_ERROR      (0x9E)
// Currently not allowed to authenticate. Keep trying until full delay is spent
#define NTAG4XX_STATUS_AUTHENTICATION_DELAY (0xAD)
// Current authentication status does not allow the requested command
#define NTAG4XX_STATUS_AUTHENTICATION_ERROR (0xAE)
// Additional data frame is expected to be sent
#define NTAG4XX_STATUS_ADDITIONAL_FRAME     (0xAF)
// Attempt to read/write data from/to beyond the file's/record's limits
// Attempt to exceed the limits of a value file.
#define NTAG4XX_STATUS_BOUNDARY_ERROR       (0xBE)
// Previous Command was not fully completed. Not all Frames were requested or provided by the PCD
#define NTAG4XX_STATUS_COMMAND_ABORTED      (0xCA)
// Specified file number does not exist
#define NTAG4XX_STATUS_FILE_NOT_FOUND       (0xF0)

// Internal helpers

Ntag4xxError ntag4xx_process_error(Iso14443_4aError error);

Ntag4xxError ntag4xx_process_status_code(uint8_t status_code);

// Parse internal Ntag4xx structures

bool ntag4xx_version_parse(Ntag4xxVersion* data, const BitBuffer* buf);

// Load internal Ntag4xx structures

bool ntag4xx_version_load(Ntag4xxVersion* data, FlipperFormat* ff);

// Save internal Ntag4xx structures

bool ntag4xx_version_save(const Ntag4xxVersion* data, FlipperFormat* ff);
