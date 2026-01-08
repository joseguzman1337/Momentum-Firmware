#pragma once
#include <furi.h>
#include <furi_hal.h>
#include <gui/gui.h>
#include "storage_glue.h"
#include "storage_sd_api.h"
#include "filesystem_api_internal.h"
#include "storage.h"

#ifdef __cplusplus
extern "C" {
#endif

#define STORAGE_COUNT (ST_INT + 1)

// Backwards-compatible aliases for legacy application asset/data paths
// used by upstream code (e.g. application_assets.c).
#define APPS_DATA_PATH   STORAGE_APPS_DATA_STEM
#define APPS_ASSETS_PATH STORAGE_APPS_ASSETS_STEM

typedef struct {
    ViewPort* view_port;
    bool enabled;
} StorageSDGui;

struct Storage {
    FuriMessageQueue* message_queue;
    StorageData storage[STORAGE_COUNT];
    StorageSDGui sd_gui;
    FuriPubSub* pubsub;
};

#ifdef __cplusplus
}
#endif
