#include <stdint.h>
#include <stdio.h>
#include <furi.h>
#include "rgb_backlight.h"

#define TAG "RGB_BACKLIGHT_SRV"

int32_t rgb_backlight_srv (void* p){
UNUSED (p);
while (1){
    FURI_LOG_I (TAG,"working");
    furi_delay_ms (2000);
}
return 0;
}