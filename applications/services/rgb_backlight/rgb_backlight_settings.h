#pragma once

#include <stdint.h>
#include <stdbool.h>

typedef struct {
    //Common settings
    uint8_t version;
    uint8_t rgb_backlight_installed;
    float brightness;
    
    // static gradient mode settings
    uint8_t static_vd1_index;
    uint8_t static_vd2_index;
    uint8_t static_vd3_index;
    
    // rainbow mode setings
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
