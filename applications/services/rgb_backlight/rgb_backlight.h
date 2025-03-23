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
    uint16_t rainbow_hue;
    uint8_t rainbow_red;
    uint8_t rainbow_green;
    uint8_t rainbow_blue;
    RGBBacklightSettings* settings;
} RGBBacklightApp;

#define RECORD_RGB_BACKLIGHT "rgb_backlight"

/** Update leds colors from current_led[i].color and selected bright
 * 
 * @param brightness  - Brightness 0..1
 * @return 
 */
void rgb_backlight_update(float brightness);

/** Set current_led[i].color for one led by static color index
 * 
 * @param led  - Led number (0..2)
 * @param index  - Static color index number
 * @return 
 */
void rgb_backlight_set_led_static_color(uint8_t led, uint8_t index);

/** Stop rainbow timer
 * 
 * @param app  - Instance of RGBBacklightApp from FURI RECORD
 * @return 
 */
void rainbow_timer_stop(RGBBacklightApp* app);

/** Start rainbow timer 
 * 
 * @param app  - Instance of RGBBacklightApp from FURI RECORD
 * @return 
 */

/** Start rainbow timer
 * 
 * @param app  - Instance of RGBBacklightApp from FURI RECORD
 * @return 
 */
void rainbow_timer_start(RGBBacklightApp* app);

/** Start rainbow timer only if all conditions meet (rgb_backlight_installed && rainbow ON)
 * 
 * @param app  - Instance of RGBBacklightApp from FURI RECORD
 * @return 
 */
void rainbow_timer_starter(RGBBacklightApp* app);

/** Get name of static color by index
 * 
 * @param index  - Static colors index number
 * @return - color name
 */
const char* rgb_backlight_get_color_text(uint8_t index);

/** Get static colors count
 * 
 * @param 
 * @return - colors count
 */
uint8_t rgb_backlight_get_color_count(void);

#ifdef __cplusplus
}
#endif
