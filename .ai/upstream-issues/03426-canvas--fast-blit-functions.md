# Issue #3426: Canvas: Fast blit function(s)

**Original Issue:** [https://github.com/flipperdevices/flipperzero-firmware/issues/3426](https://github.com/flipperdevices/flipperzero-firmware/issues/3426)
**Author:** @CookiePLMonster
**Created:** 2024-02-05T17:57:14Z
**Labels:** Feature Request, Core+Services

## Description

### Describe the enhancement you're suggesting.

Since @skotopes mentioned in [another issue](https://github.com/flipperdevices/flipperzero-firmware/issues/3380#issuecomment-1905719195) that suggestions for Canvas API expansions can be considered, an addition to allow for fast blit of a buffer on-screen would be appreciated.

Consider this demo example, based upon the Direct Draw API debug app. In this sample, I allocate a single 128x64px buffer, rasterize on it manually (in this case, a simple checkerboard, but in a real app it'd be substituted by more non-trivial workload, like in e.g. my Mode 7 demo), then I blit the buffer on screen in a single full-screen draw:

<details>
<summary>Sample app</summary>

```cpp
#include <furi.h>
#include <gui/gui.h>
#include <input/input.h>

#define BUFFER_SIZE (32U)

// This is simplified compared to the "traditional" bit band alias access, since we only occupy the bottom 256KB of SRAM anyway
#define BIT_BAND_ALIAS(var) ((uint32_t*)(((uintptr_t)(var) << 5) | 0x22000000))

[[maybe_unused]] static void canvas_blit_fast(Canvas* canvas, const uint8_t* bitmap) {
    uint8_t* buf = canvas_get_buffer(canvas);

    const uint32_t* bitmap_buffer = BIT_BAND_ALIAS(bitmap);
    uint32_t* canvas_buffer = BIT_BAND_ALIAS(buf);
    for(uint32_t y = 0; y < 64; ++y) {
        const uint32_t tile_y = ((y & 0xFFFFFFF8) << 7) | (y & 7);
        for(uint32_t x = 0; x < 128; ++x) {
            const uint32_t column = tile_y + (x * 8);
            canvas_buffer[column] = *bitmap_buffer++;
        }
    }
}

typedef struct {
    FuriPubSub* input;
    FuriPubSubSubscription* input_subscription;
    Gui* gui;
    Canvas* canvas;
    bool stop;
    uint8_t screen_buffer[16 * 64];
} DirectDraw;

static void gui_input_events_callback(const void* value, void* ctx) {
    furi_assert(value);
    furi_assert(ctx);

    DirectDraw* instance = ctx;
    const InputEvent* event = value;

    if(event->key == InputKeyBack && event->type == InputTypeShort) {
        instance->stop = true;
    }
}

static DirectDraw* direct_draw_alloc() {
    DirectDraw* instance = malloc(sizeof(DirectDraw));

    instance->input = furi_record_open(RECORD_INPUT_EVENTS);
    instance->gui = furi_record_open(RECORD_GUI);
    instance->canvas = gui_direct_draw_acquire(instance->gui);

    instance->input_subscription =
        furi_pubsub_subscribe(instance->input, gui_input_events_callback, instance);

    return instance;
}

static void direct_draw_free(DirectDraw* instance) {
    furi_pubsub_unsubscribe(instance->input, instance->input_subscription);

    instance->canvas = NULL;
    gui_direct_draw_release(instance->gui);
    furi_record_close(RECORD_GUI);
    furi_record_close(RECORD_INPUT_EVENTS);
}

static void direct_draw_run(DirectDraw* instance) {
    size_t start = DWT->CYCCNT;
    size_t counter = 0;
    float fps = 0;

    furi_thread_set_current_priority(FuriThreadPriorityIdle);

    do {
        size_t elapsed = DWT->CYCCNT - start;
        char buffer[BUFFER_SIZE] = {0};

        if(elapsed >= SystemCoreClock) {
            fps = (float)counter / ((float)elapsed / SystemCoreClock);

            start = DWT->CYCCNT;
            counter = 0;
        }
        snprintf(buffer, BUFFER_SIZE, "FPS: %.1f", (double)fps);

        // Here we would normally be doing some more complex rendering.
        // For this example, fill the bottom 3/4 of the screen with a thick checkerboard pattern
        // just to have -some- processing going on.
        {
            uint8_t* back_buffer = instance->screen_buffer + 2 * 128;
            for(uint32_t y = 16; y < 64; ++y) {
                if((y % 32) == 16) {
                    back_buffer += 2;
                } else if((y % 32) == 0) {
                    back_buffer -= 2;
                }

                for(uint32_t x = 0; x < 128; x += 32) {
                    *back_buffer++ = 0xFF;
                    *back_buffer++ = 0xFF;
                    back_buffer += 2;
                }
            }
        }

        canvas_blit_fast(instance->canvas, instance->screen_buffer);
        //canvas_draw_xbm(instance->canvas, 0, 0, 128, 64, instance->screen_buffer);

        canvas_draw_str(instance->canvas, 10, 10, buffer);
        canvas_commit(instance->canvas);

        counter++;

        furi_thread_yield();

    } while(!instance->stop);
}

int32_t fast_blit_demo_app(void* p) {
    UNUSED(p);

    DirectDraw* instance = direct_draw_alloc();
    direct_draw_run(instance);
    direct_draw_free(instance);

    return 0;
}
```
</details>

Currently, `canvas_draw_xbm` is used for tasks like this. However, u8g2 proves itself quite inefficient for a task like this that should be a glorified memcpy - instead, u8g2 appears to be drawing bit by bit.

For my proof-of-concept, I exposed `canvas_get_buffer()` to the public API. However, the memory returned by this function is tiled and therefore not user-friendly, so exposing this function is not a solution to the problem. Instead, I suggest introducing a new `blit` function that does the swizzle and assignment internally, nothing else.

I benchmarked both solutions on this app, and the results (on a `COMPACT=1` build) are as follows:
* `canvas_draw_xbm` - 39.0FPS
* `canvas_blit_fast` - ~194FPS

In a real app, the gain of `blit_fast` would likely be slightly smaller, as the call got inlined in my sample app and I have not profiled it with `noinline`. Regardless, it should still be substantial, as the function would still be subject to loop unrolling/other optimizations when part of the firmware.

### Anything else?

I'm not pressed on this being the only "correct" solution. A few other things come to mind:
* `canvas_draw_xbm` could be special-cased for fullscreen draws to do something like this.
* If compatibility with color/alpha modes is necessary, the assignment can be trivially changed from `=` to `^=` or `|=`, depending on the combination of those modes. That said, I think it would be beneficial to have a function that guarantees a copy as-is, hence the idea to differentiate `draw` functions (respecting the u8g2 state) and `blit` functions (ignoring that state by design).

---
*This issue was automatically imported from the upstream Flipper Zero firmware repository.*
