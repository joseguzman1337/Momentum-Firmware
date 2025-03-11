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

#include <furi.h>
#include "rgb_backlight_settings.h"
#include "SK6805.h"

typedef struct {
    char* name;
    uint8_t red;
    uint8_t green;
    uint8_t blue;
} RGBBacklightStaticColor;

typedef struct {
    FuriTimer* rainbow_timer;

    int16_t rainbow_red;
    int16_t rainbow_green;
    int16_t rainbow_blue;
    uint8_t rainbow_stage;

    RGBBacklightSettings* settings;

} RGBBacklightApp;

#define RECORD_RGB_BACKLIGHT "rgb_backlight"

