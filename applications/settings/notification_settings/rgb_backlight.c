/*
    RGB backlight FlipperZero driver
    Copyright (C) 2022-2023 Victor Nikitchuk (https://github.com/quen0n)

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.
*/

#include "rgb_backlight.h"
#include <furi_hal.h>
#include <storage/storage.h>

#define RGB_BACKLIGHT_SETTINGS_VERSION   6
#define RGB_BACKLIGHT_SETTINGS_FILE_NAME ".rgb_backlight.settings"
#define RGB_BACKLIGHT_SETTINGS_PATH      INT_PATH(RGB_BACKLIGHT_SETTINGS_FILE_NAME)

#define COLOR_COUNT (sizeof(colors) / sizeof(RGBBacklightColor))

#define TAG "RGB Backlight"

static RGBBacklightSettings rgb_settings = {
    .version = RGB_BACKLIGHT_SETTINGS_VERSION,
    .display_color_index = 0,
    .custom_r = 254,
    .custom_g = 254,
    .custom_b = 254,
    .settings_is_loaded = false};

static const RGBBacklightColor colors[] = {
    {"Orange", 255, 60, 0},
    {"Yellow", 255, 144, 0},
    {"Spring", 167, 255, 0},
    {"Lime", 0, 255, 0},
    {"Aqua", 0, 255, 127},
    {"Cyan", 0, 210, 210},
    {"Azure", 0, 127, 255},
    {"Blue", 0, 0, 255},
    {"Purple", 127, 0, 255},
    {"Magenta", 210, 0, 210},
    {"Pink", 255, 0, 127},
    {"Red", 255, 0, 0},
    {"White", 254, 210, 200},
    {"Custom", 0, 0, 0},
};

uint8_t rgb_backlight_get_color_count(void) {
    return COLOR_COUNT;
}

const char* rgb_backlight_get_color_text(uint8_t index) {
    return colors[index].name;
}

void rgb_backlight_load_settings(void) {
    // Do not load settings if we are in other boot modes than normal
    if(furi_hal_rtc_get_boot_mode() != FuriHalRtcBootModeNormal) {
        rgb_settings.settings_is_loaded = true;
        return;
    }

    // Wait for all required services to start and create their records
    uint8_t timeout = 0;
    while(!furi_record_exists(RECORD_STORAGE)) {
        timeout++;
        if(timeout > 150) {
            rgb_settings.settings_is_loaded = true;
            return;
        }
        furi_delay_ms(5);
    }

    RGBBacklightSettings settings;
    File* file = storage_file_alloc(furi_record_open(RECORD_STORAGE));
    const size_t settings_size = sizeof(RGBBacklightSettings);

    FURI_LOG_D(TAG, "loading settings from \"%s\"", RGB_BACKLIGHT_SETTINGS_PATH);
    bool fs_result =
        storage_file_open(file, RGB_BACKLIGHT_SETTINGS_PATH, FSAM_READ, FSOM_OPEN_EXISTING);

    if(fs_result) {
        uint16_t bytes_count = storage_file_read(file, &settings, settings_size);

        if(bytes_count != settings_size) {
            fs_result = false;
        }
    }

    if(fs_result) {
        FURI_LOG_D(TAG, "load success");
        if(settings.version != RGB_BACKLIGHT_SETTINGS_VERSION) {
            FURI_LOG_E(
                TAG,
                "version(%d != %d) mismatch",
                settings.version,
                RGB_BACKLIGHT_SETTINGS_VERSION);
        } else {
            memcpy(&rgb_settings, &settings, settings_size);
        }
    } else {
        FURI_LOG_E(TAG, "load failed, %s", storage_file_get_error_desc(file));
    }

    storage_file_close(file);
    storage_file_free(file);
    furi_record_close(RECORD_STORAGE);
    rgb_settings.settings_is_loaded = true;
}

void rgb_backlight_save_settings(void) {
    RGBBacklightSettings settings;
    File* file = storage_file_alloc(furi_record_open(RECORD_STORAGE));
    const size_t settings_size = sizeof(RGBBacklightSettings);

    FURI_LOG_D(TAG, "saving settings to \"%s\"", RGB_BACKLIGHT_SETTINGS_PATH);

    memcpy(&settings, &rgb_settings, settings_size);

    bool fs_result =
        storage_file_open(file, RGB_BACKLIGHT_SETTINGS_PATH, FSAM_WRITE, FSOM_CREATE_ALWAYS);

    if(fs_result) {
        uint16_t bytes_count = storage_file_write(file, &settings, settings_size);

        if(bytes_count != settings_size) {
            fs_result = false;
        }
    }

    if(fs_result) {
        FURI_LOG_D(TAG, "save success");
    } else {
        FURI_LOG_E(TAG, "save failed, %s", storage_file_get_error_desc(file));
    }

    storage_file_close(file);
    storage_file_free(file);
    furi_record_close(RECORD_STORAGE);
}

RGBBacklightSettings* rgb_backlight_get_settings(void) {
    if(!rgb_settings.settings_is_loaded) {
        rgb_backlight_load_settings();
    }
    return &rgb_settings;
}

void rgb_backlight_set_color(uint8_t color_index) {
    if(color_index > (rgb_backlight_get_color_count() - 1)) color_index = 0;
    rgb_settings.display_color_index = color_index;
}

void rgb_backlight_set_custom_color(uint8_t color, uint8_t index) {
    if(index > 2) return;
    if(index == 0) {
        rgb_settings.custom_r = color;
    } else if(index == 1) {
        rgb_settings.custom_g = color;
    } else if(index == 2) {
        rgb_settings.custom_b = color;
    }
}

void rgb_backlight_update(uint8_t brightness, bool bypass) {
    if(!rgb_settings.settings_is_loaded) {
        rgb_backlight_load_settings();
    }

    if(!bypass) {
        static uint8_t last_color_index = 255;
        static uint8_t last_brightness = 123;

        if(last_brightness == brightness && last_color_index == rgb_settings.display_color_index) {
            return;
        }

        last_brightness = brightness;
        last_color_index = rgb_settings.display_color_index;
    }

    for(uint8_t i = 0; i < SK6805_get_led_count(); i++) {
        if(rgb_settings.display_color_index == 13) {
            uint8_t r = rgb_settings.custom_r * (brightness / 255.0f);
            uint8_t g = rgb_settings.custom_g * (brightness / 255.0f);
            uint8_t b = rgb_settings.custom_b * (brightness / 255.0f);

            SK6805_set_led_color(i, r, g, b);
        } else {
            if((colors[rgb_settings.display_color_index].red == 0) &&
               (colors[rgb_settings.display_color_index].green == 0) &&
               (colors[rgb_settings.display_color_index].blue == 0)) {
                uint8_t r = colors[0].red * (brightness / 255.0f);
                uint8_t g = colors[0].green * (brightness / 255.0f);
                uint8_t b = colors[0].blue * (brightness / 255.0f);

                SK6805_set_led_color(i, r, g, b);
            } else {
                uint8_t r = colors[rgb_settings.display_color_index].red * (brightness / 255.0f);
                uint8_t g = colors[rgb_settings.display_color_index].green * (brightness / 255.0f);
                uint8_t b = colors[rgb_settings.display_color_index].blue * (brightness / 255.0f);

                SK6805_set_led_color(i, r, g, b);
            }
        }
    }

    SK6805_update();
}
