/**
 * Furi event loop public API.
 */
#pragma once

#include <stdint.h>
#include <stdbool.h>

#include "thread.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef struct FuriEventLoop FuriEventLoop;
typedef void FuriEventLoopObject;
typedef struct FuriEventFlag FuriEventFlag;
typedef struct FuriMessageQueue FuriMessageQueue;
typedef struct FuriStreamBuffer FuriStreamBuffer;
typedef struct FuriSemaphore FuriSemaphore;
typedef struct FuriMutex FuriMutex;

typedef enum {
    FuriEventLoopEventIn = (1 << 0),
    FuriEventLoopEventOut = (1 << 1),
    FuriEventLoopEventFlagEdge = (1 << 2),
    FuriEventLoopEventFlagOnce = (1 << 3),
} FuriEventLoopEvent;

#define FuriEventLoopEventMask (FuriEventLoopEventIn | FuriEventLoopEventOut)

typedef void (*FuriEventLoopEventCallback)(FuriEventLoopObject* object, void* context);
typedef void (*FuriEventLoopPendingCallback)(void* context);
typedef void (*FuriEventLoopThreadFlagsCallback)(void* context);
typedef void (*FuriEventLoopTickCallback)(void* context);

FuriEventLoop* furi_event_loop_alloc(void);
void furi_event_loop_free(FuriEventLoop* instance);
void furi_event_loop_run(FuriEventLoop* instance);
void furi_event_loop_stop(FuriEventLoop* instance);

void furi_event_loop_pend_callback(
    FuriEventLoop* instance,
    FuriEventLoopPendingCallback callback,
    void* context);

void furi_event_loop_subscribe_event_flag(
    FuriEventLoop* instance,
    FuriEventFlag* event_flag,
    FuriEventLoopEvent event,
    FuriEventLoopEventCallback callback,
    void* context);

void furi_event_loop_subscribe_message_queue(
    FuriEventLoop* instance,
    FuriMessageQueue* queue,
    FuriEventLoopEvent event,
    FuriEventLoopEventCallback callback,
    void* context);

void furi_event_loop_subscribe_stream_buffer(
    FuriEventLoop* instance,
    FuriStreamBuffer* stream_buffer,
    FuriEventLoopEvent event,
    FuriEventLoopEventCallback callback,
    void* context);

void furi_event_loop_subscribe_semaphore(
    FuriEventLoop* instance,
    FuriSemaphore* semaphore,
    FuriEventLoopEvent event,
    FuriEventLoopEventCallback callback,
    void* context);

void furi_event_loop_subscribe_mutex(
    FuriEventLoop* instance,
    FuriMutex* mutex,
    FuriEventLoopEvent event,
    FuriEventLoopEventCallback callback,
    void* context);

void furi_event_loop_subscribe_thread_flags(
    FuriEventLoop* instance,
    FuriEventLoopThreadFlagsCallback callback,
    void* context);

void furi_event_loop_unsubscribe_thread_flags(FuriEventLoop* instance);

void furi_event_loop_unsubscribe(FuriEventLoop* instance, FuriEventLoopObject* object);
bool furi_event_loop_is_subscribed(FuriEventLoop* instance, FuriEventLoopObject* object);

void furi_event_loop_tick_set(
    FuriEventLoop* instance,
    uint32_t interval,
    FuriEventLoopTickCallback callback,
    void* context);

#ifdef __cplusplus
}
#endif
