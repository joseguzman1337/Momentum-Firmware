#include <stdint.h>
#include <stdio.h>
#include <furi.h>
#include "rgb_backlight_settings.h"

#define TAG "RGB_BACKLIGHT_SETTINGS"

int32_t rgb_backlight_settings (void* p){
UNUSED (p);
FURI_LOG_I (TAG,"Settings");
furi_delay_ms (2000);
return 0;
}