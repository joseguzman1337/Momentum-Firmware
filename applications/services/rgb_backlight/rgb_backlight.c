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


#define PREDEFINED_COLOR_COUNT (sizeof(colors) / sizeof(RGBBacklightPredefinedColor))

#define TAG "RGB_BACKLIGHT_SRV"

static const RGBBacklightPredefinedColor colors[] = {
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
        return PREDEFINED_COLOR_COUNT;
    }

const char* rgb_backlight_get_color_text(uint8_t index) {
        return colors[index].name;
    }


void rgb_backlight_set_static_color(uint8_t index, float brightness) {
     // use RECORD for acces to rgb service instance and use current_* colors and static colors
    RGBBacklightApp* app = furi_record_open(RECORD_RGB_BACKLIGHT);
    
    for(uint8_t i = 0; i < SK6805_get_led_count(); i++) {
        app->current_red = colors[index].red;
        app->current_green = colors[index].green;
        app->current_blue = colors[index].blue;
               
        uint8_t r = app->current_red * brightness;
        uint8_t g = app->current_green * brightness;
        uint8_t b = app->current_blue * brightness;

        SK6805_set_led_color(i, r, g, b);
    }
    
    SK6805_update();
    furi_record_close(RECORD_RGB_BACKLIGHT);
}

// void rgb_backlight_set_custom_color(uint8_t red, uint8_t green, uint8_t blue, float brightness) {
//     for(uint8_t i = 0; i < SK6805_get_led_count(); i++) {
//         uint8_t r = red * (brightness);
//         uint8_t g = green * (brightness);
//         uint8_t b = blue * (brightness);
//         SK6805_set_led_color(i, r, g, b);
//     }
//     SK6805_update();
// }

// apply new brightness to current display color set
void rgb_backlight_update (float brightness) {
    // use RECORD for acces to rgb service instance and use current_* colors
    RGBBacklightApp* app = furi_record_open(RECORD_RGB_BACKLIGHT);
    
    for(uint8_t i = 0; i < SK6805_get_led_count(); i++) {
        uint8_t r = app->current_red * brightness;
        uint8_t g = app->current_green * brightness;
        uint8_t b = app->current_blue * brightness;
        SK6805_set_led_color(i, r, g, b);
    }

    furi_record_close(RECORD_RGB_BACKLIGHT);
    SK6805_update();
}
//start furi timer for rainbow
void rainbow_timer_start(RGBBacklightApp* app) {
    furi_timer_start(
        app->rainbow_timer, furi_ms_to_ticks(app->settings->rainbow_speed_ms));
}

//stop furi timer for rainbow
void rainbow_timer_stop(RGBBacklightApp* app) {
    furi_timer_stop(app->rainbow_timer);
}

// if rgb_mod_installed then apply rainbow colors to backlight and start/restart/stop rainbow_timer
void rainbow_timer_starter(RGBBacklightApp* app) {
    if(app->settings->rgb_mod_installed) {
        if(app->settings->rainbow_mode > 0) {
            // rgb_backlight_set_custom_color(
            //     app->rainbow_red,
            //     app->rainbow_green,
            //     app->rainbow_blue,
            //     app->settings->brightness);
            rainbow_timer_start(app);
        } else {
            if(furi_timer_is_running(app->rainbow_timer)) {
                rainbow_timer_stop(app);
            }
        }
    }
}

static void rainbow_timer_callback(void* context) {
    furi_assert(context);
    RGBBacklightApp* app = context;

    // if rgb_mode_rainbow_mode is rainbow do rainbow effect
    if(app->settings->rainbow_mode == 1) {
        switch(app->rainbow_stage) {
        // from red to yellow (255,0,0) - (255,255,0)
        case 1:
            app->current_green += app->settings->rainbow_step;
            if(app->current_green >= 255) {
                app->current_green = 255;
                app->rainbow_stage++;
            }
            break;
        // yellow to green (255,255,0) - (0,255,0)
        case 2:
            app->current_red -= app->settings->rainbow_step;
            if(app->current_red <= 0) {
                app->current_red = 0;
                app->rainbow_stage++;
            }
            break;
        // from green to light blue (0,255,0) - (0,255,255)
        case 3:
            app->current_blue += app->settings->rainbow_step;
            if(app->current_blue >= 255) {
                app->current_blue = 255;
                app->rainbow_stage++;
            }
            break;
        //from light blue to blue (0,255,255) - (0,0,255)
        case 4:
            app->current_green -= app->settings->rainbow_step;
            if(app->current_green <= 0) {
                app->current_green = 0;
                app->rainbow_stage++;
            }
            break;
        //from blue to violet (0,0,255) - (255,0,255)
        case 5:
            app->current_red += app->settings->rainbow_step;
            if(app->current_red >= 255) {
                app->current_red = 255;
                app->rainbow_stage++;
            }
            break;
        //from violet to red (255,0,255) - (255,0,0)
        case 6:
            app->current_blue -= app->settings->rainbow_step;
            if(app->current_blue <= 0) {
                app->current_blue = 0;
                app->rainbow_stage = 1;
            }
            break;
        default:
            break;
        }

    //     rgb_backlight_set_custom_color(
    //         app->current_red,
    //         app->current_green,
    //         app->current_blue,
    //         app->settings->brightness);
    }
    
    rgb_backlight_update (app->settings->brightness);

    // if rgb_mode_rainbow_mode is ..... do another effect
    // if(app->settings.rainbow_mode == 2) {
    // }
}

int32_t rgb_backlight_srv (void* p) {
    UNUSED(p);

    // Define object app (full app with settings and running variables), 
    // allocate memory and create record for access to app structure from outside
    RGBBacklightApp* app = malloc(sizeof(RGBBacklightApp));

    furi_record_create(RECORD_RGB_BACKLIGHT, app);

    //define rainbow_timer and they callback
    app->rainbow_timer =
        furi_timer_alloc(rainbow_timer_callback, FuriTimerTypePeriodic, app);

    // settings load or create default
    app->settings = malloc(sizeof(RGBBacklightSettings));
    rgb_backlight_settings_load (app->settings);

    // Init app variables
    app->current_red = 255;
    app->current_green = 60;
    app->current_blue = 0;
    app->rainbow_stage = 1;

    // а нужно ли это все при старте сервиса, если мы получим сигнал на подсветку от Нотификейшена. Может вынести в ИНИТ и при старте нотиф дернуть его 1 раз
    // if rgb_mod_installed start rainbow or set static color from settings (default index = 0)
    if(app->settings->rgb_mod_installed) {
        if(app->settings->rainbow_mode > 0 ) {
            rainbow_timer_starter(app);
        } else {
            rgb_backlight_set_static_color(app->settings->static_color_index, app->settings->brightness);
        }
    // if not rgb_mod_installed set default static orange color (index=0)
    } else {
        rgb_backlight_set_static_color(0, app->settings->brightness);
    }        

    while(1) {
        FURI_LOG_I(TAG, "working");
        furi_delay_ms(2000);
    }
    return 0;
}