/*
    RGB BackLight Service based on 
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

#include <stdint.h>
#include <stdio.h>
#include <furi.h>
#include <furi_hal.h>
#include <storage/storage.h>
#include "rgb_backlight.h"

#define COLOR_COUNT (sizeof(colors) / sizeof(RGBBacklightColor))

#define TAG "RGB_BACKLIGHT_SRV"

typedef struct {
    char* name;
    uint8_t red;
    uint8_t green;
    uint8_t blue;
} RGBBacklightColor;

//use one type RGBBacklightColor for current_leds_settings and for static colors definition
static RGBBacklightColor current_led [] = {
    {"LED0",255,60,0},
    {"LED1",255,60,0},
    {"LED2",255,60,0},
};

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
    {"OFF", 0, 0, 0},
};

uint8_t rgb_backlight_get_color_count(void) {
    return COLOR_COUNT;
}

const char* rgb_backlight_get_color_text(uint8_t index) {
    return colors[index].name;
}

// use RECORD for acces to rgb service instance and update current colors by static
void rgb_backlight_set_led_static_color(uint8_t led, uint8_t index) {
    // RGBBacklightApp* app = furi_record_open(RECORD_RGB_BACKLIGHT);
    // float brightness = app->settings->brightness;

    if(led < SK6805_get_led_count()) {
        uint8_t r = colors[index].red;
        uint8_t g = colors[index].green;
        uint8_t b = colors[index].blue;
        
        current_led[led].red = r; 
        current_led[led].green =g;
        current_led[led].blue = b;

        SK6805_set_led_color(led, r, g, b);
    }

    // furi_record_close(RECORD_RGB_BACKLIGHT);
}

// use RECORD for acces to rgb service instance and update current colors by custom
// void rgb_backlight_set_custom_color(uint8_t red, uint8_t green, uint8_t blue) {
//     RGBBacklightApp* app = furi_record_open(RECORD_RGB_BACKLIGHT);
//     app->current_red = red;
//     app->current_green = green;
//     app->current_blue = blue;
//     furi_record_close(RECORD_RGB_BACKLIGHT);
// }

// use RECORD for acces to rgb service instance, use current_* colors and update backlight
void rgb_backlight_update(float brightness) {
    RGBBacklightApp* app = furi_record_open(RECORD_RGB_BACKLIGHT);
    
    if(app->settings->rgb_backlight_installed) {
        for(uint8_t i = 0; i < SK6805_get_led_count(); i++) {
            uint8_t r = current_led[i].red * (brightness * 1.0f);
            uint8_t g = current_led[i].green * (brightness * 1.0f);
            uint8_t b = current_led[i].blue * (brightness * 1.0f);
            SK6805_set_led_color(i, r, g, b);
        }
        SK6805_update();
    }
    furi_record_close(RECORD_RGB_BACKLIGHT);
}

//start furi timer for rainbow
void rainbow_timer_start(RGBBacklightApp* app) {
    furi_timer_start(app->rainbow_timer, furi_ms_to_ticks(app->settings->rainbow_speed_ms));
}

//stop furi timer for rainbow
void rainbow_timer_stop(RGBBacklightApp* app) {
    furi_timer_stop(app->rainbow_timer);
}

// if rgb_backlight_installed then apply rainbow colors to backlight and start/restart/stop rainbow_timer
void rainbow_timer_starter(RGBBacklightApp* app) {
    if((app->settings->rainbow_mode > 0) && (app->settings->rgb_backlight_installed)) {
        rainbow_timer_start(app);
    } else {
        if(furi_timer_is_running(app->rainbow_timer)) {
            rainbow_timer_stop(app);
        }
    }
}
static void rainbow_timer_callback(void* context) {
    furi_assert(context);
    RGBBacklightApp* app = context;

    if (app->settings->rgb_backlight_installed) {
        switch(app->settings->rainbow_mode) { 
            case 1:
                break;
            case 2:
                break;
            default:
                break;
        }
        rgb_backlight_update(app->settings->brightness);
    }

    // if rainbow_mode is ..... do another effect
    // if(app->settings.rainbow_mode == ...) {
    // }

}

int32_t rgb_backlight_srv(void* p) {
    UNUSED(p);

    // Define object app (full app with settings and running variables),
    // allocate memory and create RECORD for access to app structure from outside
    RGBBacklightApp* app = malloc(sizeof(RGBBacklightApp));
    
    //define rainbow_timer and they callback
    app->rainbow_timer = furi_timer_alloc(rainbow_timer_callback, FuriTimerTypePeriodic, app);

    // settings load or create default
    app->settings = malloc(sizeof(RGBBacklightSettings));
    rgb_backlight_settings_load(app->settings);

    furi_record_create(RECORD_RGB_BACKLIGHT, app);

    //if rgb_backlight_installed then start rainbow or set leds colors from saved settings (default index = 0)
    if(app->settings->rgb_backlight_installed) {
        if(app->settings->rainbow_mode > 0) {
            // rainbow_timer_starter(app);
        } else {
            rgb_backlight_set_led_static_color (2,app->settings->led_2_color_index);
            rgb_backlight_set_led_static_color (1,app->settings->led_1_color_index);
            rgb_backlight_set_led_static_color (0,app->settings->led_0_color_index);
            rgb_backlight_update (app->settings->brightness);
        }
    // if rgb_backlight not installed then set default static orange color(index=0) to all leds (0-2) and force light on
    } else {
        rgb_backlight_set_led_static_color (2,0);
        rgb_backlight_set_led_static_color (1,0);
        rgb_backlight_set_led_static_color (0,0);
        SK6805_update();
    }

    while(1) {
        // place for message queue and other future options
        furi_delay_ms (5000);
        if(app->settings->rgb_backlight_installed) {
            FURI_LOG_D(TAG, "RGB backlight enabled - serivce is running");
        } else {
            FURI_LOG_D(TAG, "RGB backlight DISABLED - serivce is running");
        }
    }
    return 0;
}
