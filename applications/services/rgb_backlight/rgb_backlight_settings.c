#include "rgb_backlight_settings.h"

#include <saved_struct.h>
#include <storage/storage.h>

#define TAG "RGBBackligthSettings"

#define RGB_BACKLIGHT_SETTINGS_FILE_NAME ".rgb_backlight.settings"
#define RGB_BACKLIGHT_SETTINGS_PATH      INT_PATH(RGB_BACKLIGHT_SETTINGS_FILE_NAME)

#define RGB_BACKLIGHT_SETTINGS_MAGIC    (0x30)
#define RGB_BACKLIGHT_SETTINGS_VER_PREV (0) // Previous version number
#define RGB_BACKLIGHT_SETTINGS_VER      (1) // New version number

//pervious settings must be copyed from previous rgb_backlight_settings.h file
typedef struct {
    uint8_t version;
    bool rgb_mod_installed;

    uint8_t static_color_index;
    uint8_t custom_r;
    uint8_t custom_g;
    uint8_t custom_b;

    uint32_t rainbow_mode;
    uint32_t rainbow_speed_ms;
    uint16_t rainbow_step;
} RGBBacklightSettingsPrevious;

void rgb_backlight_settings_load(RGBBacklightSettings* settings) {
    furi_assert(settings);

    bool success = false;

    //a useless cycle do-while, may will be used in future with anoter condition
    do {
        // take version from settings file metadata, if cant then break and fill settings with 0 and save to settings file;
        uint8_t version;
        if(!saved_struct_get_metadata(RGB_BACKLIGHT_SETTINGS_PATH, NULL, &version, NULL)) break;

        // if config actual version - load it directly
        if(version == RGB_BACKLIGHT_SETTINGS_VER) {
            success = saved_struct_load(
                RGB_BACKLIGHT_SETTINGS_PATH,
                settings,
                sizeof(RGBBacklightSettings),
                RGB_BACKLIGHT_SETTINGS_MAGIC,
                RGB_BACKLIGHT_SETTINGS_VER);
            // if config previous version - load it and inicialize new settings
        } else if(version == RGB_BACKLIGHT_SETTINGS_VER_PREV) {
            RGBBacklightSettingsPrevious* settings_previous =
                malloc(sizeof(RGBBacklightSettingsPrevious));

            success = saved_struct_load(
                RGB_BACKLIGHT_SETTINGS_PATH,
                settings_previous,
                sizeof(RGBBacklightSettingsPrevious),
                RGB_BACKLIGHT_SETTINGS_MAGIC,
                RGB_BACKLIGHT_SETTINGS_VER_PREV);
            // new settings initialization
            if(success) {
                // copy loaded old settings as part of new
                uint32_t size = sizeof(settings);
                memcpy(settings, settings_previous, size);
                // set new options to initial value
                // settings.something = something;
            }

            free(settings_previous);
        }
        // in case of another config version we exit from useless cycle to next step
    } while(false);

    // fill settings with 0 and save to settings file;
    // Orange color (index=0) will be default
    if(!success) {
        FURI_LOG_W(TAG, "Failed to load file, using defaults");
        memset(settings, 0, sizeof(RGBBacklightSettings));
        settings->brightness = 1.0f;
        settings->rainbow_speed_ms = 100;
        settings->rainbow_step = 1;
        rgb_backlight_settings_save(settings);
    }
}

void rgb_backlight_settings_save(const RGBBacklightSettings* settings) {
    furi_assert(settings);

    const bool success = saved_struct_save(
        RGB_BACKLIGHT_SETTINGS_PATH,
        settings,
        sizeof(RGBBacklightSettings),
        RGB_BACKLIGHT_SETTINGS_MAGIC,
        RGB_BACKLIGHT_SETTINGS_VER);

    if(!success) {
        FURI_LOG_E(TAG, "Failed to save rgb_backlight_settings file");
    } else {
        FURI_LOG_I(TAG, "Settings saved");
    }
}
