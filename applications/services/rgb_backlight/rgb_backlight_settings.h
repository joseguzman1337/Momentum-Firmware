#pragma once

#include <stdint.h>
#include <stdbool.h>

typedef struct {
    uint8_t version;
    bool rgb_mod_installed;

    uint8_t display_static_color_index;
    uint8_t custom_r;
    uint8_t custom_g;
    uint8_t custom_b;
    float brightness;

    uint32_t rainbow_mode;
    uint32_t rainbow_speed_ms;
    uint16_t rainbow_step;

} RGBBacklightSettings;

#ifdef __cplusplus
extern "C" {
#endif

void rgb_backlight_settings_load(RGBBacklightSettings* settings);
void rgb_backlight_settings_save(const RGBBacklightSettings* settings);

#ifdef __cplusplus
}
#endif
