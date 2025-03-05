#pragma once

#include "type_4_tag.h"

#include <lib/nfc/protocols/iso14443_4a/iso14443_4a_poller.h>

#ifdef __cplusplus
extern "C" {
#endif

/**
 * @brief Type4TagPoller opaque type definition.
 */
typedef struct Type4TagPoller Type4TagPoller;

/**
 * @brief Enumeration of possible Type4Tag poller event types.
 */
typedef enum {
    Type4TagPollerEventTypeReadSuccess, /**< Card was read successfully. */
    Type4TagPollerEventTypeReadFailed, /**< Poller failed to read card. */
} Type4TagPollerEventType;

/**
 * @brief Type4Tag poller event data.
 */
typedef union {
    Type4TagError error; /**< Error code indicating card reading fail reason. */
} Type4TagPollerEventData;

/**
 * @brief Type4Tag poller event structure.
 *
 * Upon emission of an event, an instance of this struct will be passed to the callback.
 */
typedef struct {
    Type4TagPollerEventType type; /**< Type of emmitted event. */
    Type4TagPollerEventData* data; /**< Pointer to event specific data. */
} Type4TagPollerEvent;

#ifdef __cplusplus
}
#endif
