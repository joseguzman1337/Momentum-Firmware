#pragma once

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

#include <furi/core/core_defines.h>
#include <gui/canvas.h>
#include <gui/icon_i.h>
#include <m-list.h>

#ifdef __cplusplus
extern "C" {
#endif

typedef struct StorageAnimation StorageAnimation;

typedef struct {
    const char* name;
    uint32_t min_butthurt;
    uint32_t max_butthurt;
    uint32_t min_level;
    uint32_t max_level;
    uint32_t weight;
} StorageAnimationManifestInfo;

typedef struct {
    uint32_t x;
    uint32_t y;
    const char* text;
    Align align_h;
    Align align_v;
} Bubble;

typedef struct FrameBubble {
    Bubble bubble;
    uint32_t start_frame;
    uint32_t end_frame;
    const struct FrameBubble* next_bubble;
} FrameBubble;

typedef struct {
    struct Icon icon_animation;
    const uint8_t* frame_order;
    uint8_t passive_frames;
    uint8_t active_frames;
    uint8_t active_cycles;
    uint32_t duration;
    uint32_t active_cooldown;
    const FrameBubble* const* frame_bubble_sequences;
    uint8_t frame_bubble_sequences_count;
} BubbleAnimation;

LIST_DEF(StorageAnimationList, StorageAnimation*, M_PTR_OPLIST);

void animation_storage_fill_animation_list(StorageAnimationList_t* animation_list);
StorageAnimation* animation_storage_find_animation(const char* name);
StorageAnimationManifestInfo* animation_storage_get_meta(StorageAnimation* storage_animation);
const BubbleAnimation* animation_storage_get_bubble_animation(StorageAnimation* storage_animation);
void animation_storage_cache_animation(StorageAnimation* storage_animation);
void animation_storage_free_storage_animation(StorageAnimation** storage_animation);

#ifdef __cplusplus
}
#endif
