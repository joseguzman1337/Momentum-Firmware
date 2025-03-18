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

#pragma once
#include <furi.h>
#include "rgb_backlight_settings.h"
#include "SK6805.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef struct {
    FuriTimer* rainbow_timer;

    // int16_t current_red;
    // int16_t current_green;
    // int16_t current_blue;

    RGBBacklightSettings* settings;

} RGBBacklightApp;

#define RECORD_RGB_BACKLIGHT "rgb_backlight"

void rgb_backlight_update(float brightness);
// void rgb_backlight_set_custom_color(uint8_t red, uint8_t green, uint8_t blue);
void rgb_backlight_set_led_static_color(uint8_t led, uint8_t index);
void rainbow_timer_stop(RGBBacklightApp* app);
void rainbow_timer_start(RGBBacklightApp* app);
void rainbow_timer_starter(RGBBacklightApp* app);
const char* rgb_backlight_get_color_text(uint8_t index);
uint8_t rgb_backlight_get_color_count(void);

#ifdef __cplusplus
}
#endif
