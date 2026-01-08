/**
 * @file canvas.h
 * GUI: Canvas API
 */

#pragma once

#include <stddef.h>
#include <stdint.h>
#include <gui/icon.h>
#include <gui/icon_animation.h>

#ifdef __cplusplus
extern "C" {
#endif

/** Color enumeration */
typedef enum {
    ColorWhite = 0x00,
    ColorBlack = 0x01,
    ColorXOR = 0x02,
} Color;

/** Fonts enumeration */
typedef enum {
    FontPrimary,
    FontSecondary,
    FontKeyboard,
    FontBigNumbers,

    // Keep last for fonts number calculation
    FontTotalNumber,
} Font;

/** Alignment enumeration */
typedef enum {
    AlignLeft,
    AlignRight,
    AlignTop,
    AlignBottom,
    AlignCenter,
} Align;

/** Canvas Orientation */
typedef enum {
    CanvasOrientationHorizontal,
    CanvasOrientationHorizontalFlip,
    CanvasOrientationVertical,
    CanvasOrientationVerticalFlip,
} CanvasOrientation;

/** Font Direction */
typedef enum {
    CanvasDirectionLeftToRight,
    CanvasDirectionTopToBottom,
    CanvasDirectionRightToLeft,
    CanvasDirectionBottomToTop,
} CanvasDirection;

/** Font parameters */
typedef struct {
    uint8_t leading_default;
    uint8_t leading_min;
    uint8_t height;
    uint8_t descender;
} CanvasFontParameters;

/** Icon flip */
typedef enum {
    IconFlipNone,
    IconFlipHorizontal,
    IconFlipVertical,
    IconFlipBoth,
} IconFlip;

/** Icon rotation */
typedef enum {
    IconRotation0,
    IconRotation90,
    IconRotation180,
    IconRotation270,
} IconRotation;

/** Canvas anonymous structure */
typedef struct Canvas Canvas;

/** Reset canvas drawing tools configuration
 *
 * @param      canvas  Canvas instance
 */
void canvas_reset(Canvas* canvas);

/** Commit canvas. Send buffer to display
 *
 * @param      canvas  Canvas instance
 */
void canvas_commit(Canvas* canvas);

/** Get Canvas width
 *
 * @param      canvas  Canvas instance
 *
 * @return     width in pixels.
 */
size_t canvas_width(const Canvas* canvas);

/** Get Canvas height
 *
 * @param      canvas  Canvas instance
 *
 * @return     height in pixels.
 */
size_t canvas_height(const Canvas* canvas);

/** Get current font height
 *
 * @param      canvas  Canvas instance
 *
 * @return     height in pixels.
 */
size_t canvas_current_font_height(const Canvas* canvas);

/** Get font parameters
 *
 * @param      canvas  Canvas instance
 * @param      font    Font
 *
 * @return     pointer to CanvasFontParameters structure
 */
const CanvasFontParameters* canvas_get_font_params(const Canvas* canvas, Font font);

/** Clear canvas
 *
 * @param      canvas  Canvas instance
 */
void canvas_clear(Canvas* canvas);

/** Set drawing color
 *
 * @param      canvas  Canvas instance
 * @param      color   Color
 */
void canvas_set_color(Canvas* canvas, Color color);

/** Set font swap Argument String Rotation Description
 *
 * @param      canvas  Canvas instance
 * @param      dir     Direction font
 */
void canvas_set_font_direction(Canvas* canvas, CanvasDirection dir);

/** Invert drawing color
 *
 * @param      canvas  Canvas instance
 */
void canvas_invert_color(Canvas* canvas);

/** Set drawing font
 *
 * @param      canvas  Canvas instance
 * @param      font    Font
 */
void canvas_set_font(Canvas* canvas, Font font);

/** Set custom drawing font
 *
 * @param      canvas  Canvas instance
 * @param      font    Pointer to u8g2 const uint8_t* font array
 */
void canvas_set_custom_u8g2_font(Canvas* canvas, const uint8_t* font);

/** Draw string at position of baseline defined by x, y.
 *
 * @param      canvas  Canvas instance
 * @param      x       anchor point x coordinate
 * @param      y       anchor point y coordinate
 * @param      str     C-string
 */
void canvas_draw_str(Canvas* canvas, int32_t x, int32_t y, const char* str);

/** Draw aligned string defined by x, y.
 *
 * Align calculated from position of baseline, string width and ascent (height
 * of the glyphs above the baseline)
 *
 * @param      canvas      Canvas instance
 * @param      x           anchor point x coordinate
 * @param      y           anchor point y coordinate
 * @param      horizontal  horizontal alignment
 * @param      vertical    vertical alignment
 * @param      str         C-string
 */
void canvas_draw_str_aligned(
    Canvas* canvas,
    int32_t x,
    int32_t y,
    Align horizontal,
    Align vertical,
    const char* str);

/** Draw circle
 *
 * @param      canvas  Canvas instance
 * @param      x       x coordinate
 * @param      y       y coordinate
 * @param      radius  radius
 */
void canvas_draw_circle(Canvas* canvas, int32_t x, int32_t y, size_t radius);

/** Draw disc
 *
 * @param      canvas  Canvas instance
 * @param      x       x coordinate
 * @param      y       y coordinate
 * @param      radius  radius
 */
void canvas_draw_disc(Canvas* canvas, int32_t x, int32_t y, size_t radius);

/** Draw a square frame with rounded corners
 *
 * @param      canvas  Canvas instance
 * @param      x       x coordinate
 * @param      y       y coordinate
 * @param      w       width
 * @param      h       height
 * @param      r       radius
 */
void canvas_draw_rframe(Canvas* canvas, int32_t x, int32_t y, size_t w, size_t h, size_t r);

/** Draw a filled square with rounded corners
 *
 * @param      canvas  Canvas instance
 * @param      x       x coordinate
 * @param      y       y coordinate
 * @param      w       width
 * @param      h       height
 * @param      r       radius
 */
void canvas_draw_rbox(Canvas* canvas, int32_t x, int32_t y, size_t w, size_t h, size_t r);

/** Draw a frame
 *
 * @param      canvas  Canvas instance
 * @param      x       x coordinate
 * @param      y       y coordinate
 * @param      w       width
 * @param      h       height
 */
void canvas_draw_frame(Canvas* canvas, int32_t x, int32_t y, size_t w, size_t h);

/** Draw a filled box
 *
 * @param      canvas  Canvas instance
 * @param      x       x coordinate
 * @param      y       y coordinate
 * @param      w       width
 * @param      h       height
 */
void canvas_draw_box(Canvas* canvas, int32_t x, int32_t y, size_t w, size_t h);

/** Draw a line
 *
 * @param      canvas  Canvas instance
 * @param      x1      x coordinate of first point
 * @param      y1      y coordinate of first point
 * @param      x2      x coordinate of second point
 * @param      y2      y coordinate of second point
 */
void canvas_draw_line(Canvas* canvas, int32_t x1, int32_t y1, int32_t x2, int32_t y2);

/** Draw a dot
 *
 * @param      canvas  Canvas instance
 * @param      x       x coordinate
 * @param      y       y coordinate
 */
void canvas_draw_dot(Canvas* canvas, int32_t x, int32_t y);

/** Draw a 1-bit bitmap with specified width, height.
 * @warning bitmap data must be in 8-bit boundary by width.
 * @param canvas    Canvas instance
 * @param x         x coordinate
 * @param y         y coordinate
 * @param width     width
 * @param height    height
 * @param data      bitmap data
 */
void canvas_draw_bitmap(
    Canvas* canvas,
    int32_t x,
    int32_t y,
    size_t width,
    size_t height,
    const uint8_t* data);

/** Draw Icon
 *
 * @param      canvas  Canvas instance
 * @param      x       x coordinate
 * @param      y       y coordinate
 * @param      icon    Icon pointer
 */
void canvas_draw_icon(Canvas* canvas, int32_t x, int32_t y, const Icon* icon);

/** Draw Icon with flip
 *
 * @param      canvas  Canvas instance
 * @param      x       x coordinate
 * @param      y       y coordinate
 * @param      icon    Icon pointer
 * @param      flip    Icon flip
 */
void canvas_draw_icon_ex(
    Canvas* canvas,
    int32_t x,
    int32_t y,
    const Icon* icon,
    IconFlip flip);

/** Draw Icon with rotation
 *
 * @param      canvas  Canvas instance
 * @param      x       x coordinate
 * @param      y       y coordinate
 * @param      icon    Icon pointer
 * @param      rotation    Icon rotation
 */
void canvas_draw_icon_rotate(
    Canvas* canvas,
    int32_t x,
    int32_t y,
    const Icon* icon,
    IconRotation rotation);

/** Draw Icon Animation
 *
 * @param      canvas  Canvas instance
 * @param      x       x coordinate
 * @param      y       y coordinate
 * @param      animation    Icon Animation pointer
 */
void canvas_draw_icon_animation(
    Canvas* canvas,
    int32_t x,
    int32_t y,
    IconAnimation* animation);

/** Draw XBM icon with specified width, height.
 *
 * @warning icon data must be in 8-bit boundary by width.
 * @param canvas    Canvas instance
 * @param x         x coordinate
 * @param y         y coordinate
 * @param width     width
 * @param height    height
 * @param data      icon data
 */
void canvas_draw_xbm(Canvas* canvas, int32_t x, int32_t y, size_t width, size_t height, const uint8_t* data);

/** Draw XBM icon with specified width, height and rotation.
 *
 * @warning icon data must be in 8-bit boundary by width.
 * @param canvas    Canvas instance
 * @param x         x coordinate
 * @param y         y coordinate
 * @param width     width
 * @param height    height
 * @param data      icon data
 * @param rotation  rotation
 */
void canvas_draw_xbm_rotated(
    Canvas* canvas,
    int32_t x,
    int32_t y,
    size_t width,
    size_t height,
    const uint8_t* data,
    IconRotation rotation);

#ifdef __cplusplus
}
#endif
