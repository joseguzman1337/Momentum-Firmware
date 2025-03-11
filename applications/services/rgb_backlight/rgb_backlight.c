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


#define STATIC_COLOR_COUNT (sizeof(colors) / sizeof(RGBBacklightStaticColor))

#define TAG "RGB_BACKLIGHT_SRV"

static const RGBBacklightStaticColor colors[] = {
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

void rgb_backlight_set_custom_color(uint8_t red, uint8_t green, uint8_t blue, float brightness) {
    for(uint8_t i = 0; i < SK6805_get_led_count(); i++) {
        uint8_t r = red * (brightness);
        uint8_t g = green * (brightness);
        uint8_t b = blue * (brightness);
        SK6805_set_led_color(i, r, g, b);
    }
    SK6805_update();
}

static void rainbow_timer_callback(void* context) {
    furi_assert(context);
    RGBBacklightApp* app = context;

    // if rgb_mode_rainbow_mode is rainbow do rainbow effect
    if(app->settings->rainbow_mode == 1) {
        switch(app->rainbow_stage) {
        // from red to yellow
        case 1:
            app->rainbow_green += app->settings->rainbow_step;
            if(app->rainbow_green >= 255) {
                app->rainbow_green = 255;
                app->rainbow_stage++;
            }
            break;
        // yellow red to green
        case 2:
            app->rainbow_red -= app->settings->rainbow_step;
            if(app->rainbow_red <= 0) {
                app->rainbow_red = 0;
                app->rainbow_stage++;
            }
            break;
        // from green to light blue
        case 3:
            app->rainbow_blue += app->settings->rainbow_step;
            if(app->rainbow_blue >= 255) {
                app->rainbow_blue = 255;
                app->rainbow_stage++;
            }
            break;
        //from light blue to blue
        case 4:
            app->rainbow_green -= app->settings->rainbow_step;
            if(app->rainbow_green <= 0) {
                app->rainbow_green = 0;
                app->rainbow_stage++;
            }
            break;
        //from blue to violet
        case 5:
            app->rainbow_red += app->settings->rainbow_step;
            if(app->rainbow_red >= 255) {
                app->rainbow_red = 255;
                app->rainbow_stage++;
            }
            break;
        //from violet to red
        case 6:
            app->rainbow_blue -= app->settings->rainbow_step;
            if(app->rainbow_blue <= 0) {
                app->rainbow_blue = 0;
                app->rainbow_stage = 1;
            }
            break;
        default:
            break;
        }

        rgb_backlight_set_custom_color(
            app->rainbow_red,
            app->rainbow_green,
            app->rainbow_blue,
            app->settings->brightness);
    }

    // if rgb_mode_rainbow_mode is ..... do another effect
    // if(app->settings.rainbow_mode == 2) {
    // }
}

void rgb_backlight_settings_apply(RGBBacklightSettings* settings) {
    UNUSED (settings);
    //запуск таймера если все включено
    // применить сохраненые настройки цвета к дисплею статику или кастом если индекс=13
}

int32_t rgb_backlight_srv (void* p){
    // Define object app (full app with settings and running variables), 
    // allocate memory and create record for access to app structure from outside
    RGBBacklightApp* app = malloc(sizeof(RGBBacklightApp));
    furi_record_create(RECORD_RGB_BACKLIGHT, app);

    //define rainbow_timer and they callback
    app->rainbow_timer =
        furi_timer_alloc(rainbow_timer_callback, FuriTimerTypePeriodic, app);

    // load or init new settings and apply it
    rgb_backlight_settings_load (app->settings);
    rgb_backlight_settings_apply (app->settings);

    UNUSED(p);
    while(1) {
        FURI_LOG_I(TAG, "working");
        furi_delay_ms(2000);
    }
    return 0;
}