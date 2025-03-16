
#include <furi.h>
#include <storage/storage.h>
#include "applications/services/rgb_backlight/rgb_backlight.h"

static int32_t boot_rgb_backlight_update(void* context) {
    UNUSED(context);
    RGBBacklightApp* app = furi_record_open(RECORD_RGB_BACKLIGHT);
    if(!app->settings->rgb_mod_installed) {
        rgb_backlight_set_static_color(0);
        for(uint8_t i = 0; i < SK6805_get_led_count(); i++) {
            uint8_t r = app->current_red * (1.0f / 1.0f);
            uint8_t g = app->current_green * (1.0f / 1.0f);
            uint8_t b = app->current_blue * (1.0f / 1.0f);
            SK6805_set_led_color(i, r, g, b);
        }
        SK6805_update();
    }
    furi_record_close(RECORD_RGB_BACKLIGHT);
    return 0;
}

static void
    rgb_boot_loader_release_callback(FuriThread* thread, FuriThreadState state, void* context) {
    UNUSED(context);

    if(state == FuriThreadStateStopped) {
        furi_thread_free(thread);
    }
}

static void rgb_boot_storage_callback(const void* message, void* context) {
    UNUSED(context);
    const StorageEvent* event = message;

    if(event->type == StorageEventTypeCardMount) {
        FuriThread* loader = furi_thread_alloc_ex(NULL, 2048, boot_rgb_backlight_update, NULL);
        furi_thread_set_state_callback(loader, rgb_boot_loader_release_callback);
        furi_thread_start(loader);
    }
}

int32_t rgb_backlight_on_system_start(void* p) {
    UNUSED(p);

    Storage* storage = furi_record_open(RECORD_STORAGE);
    furi_pubsub_subscribe(storage_get_pubsub(storage), rgb_boot_storage_callback, NULL);

    if(storage_sd_status(storage) != FSE_OK) {
        FURI_LOG_D("RGB_Boot_Init", "SD Card not ready, skipping rgb backlight init");
        return 0;
    }

    boot_rgb_backlight_update(NULL);
    return 0;
}
