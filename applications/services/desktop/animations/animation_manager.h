#pragma once

#include <stdbool.h>

#include "animation_storage.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef struct AnimationManager AnimationManager;
typedef struct View View;

typedef void (*AnimationManagerSetNewIdleAnimationCallback)(void* context);
typedef void (*AnimationManagerCheckBlockingCallback)(void* context);
typedef void (*AnimationManagerInteractCallback)(void* context);

AnimationManager* animation_manager_alloc(void);
void animation_manager_free(AnimationManager* animation_manager);

void animation_manager_set_context(AnimationManager* animation_manager, void* context);
void animation_manager_set_new_idle_callback(
    AnimationManager* animation_manager,
    AnimationManagerSetNewIdleAnimationCallback callback);
void animation_manager_set_check_callback(
    AnimationManager* animation_manager,
    AnimationManagerCheckBlockingCallback callback);
void animation_manager_set_interact_callback(
    AnimationManager* animation_manager,
    AnimationManagerInteractCallback callback);
void animation_manager_set_dummy_mode_state(AnimationManager* animation_manager, bool enabled);

void animation_manager_check_blocking_process(AnimationManager* animation_manager);
void animation_manager_new_idle_process(AnimationManager* animation_manager);
bool animation_manager_interact_process(AnimationManager* animation_manager);

View* animation_manager_get_animation_view(AnimationManager* animation_manager);
bool animation_manager_is_animation_loaded(AnimationManager* animation_manager);
void animation_manager_unload_and_stall_animation(AnimationManager* animation_manager);
void animation_manager_load_and_continue_animation(AnimationManager* animation_manager);

#ifdef __cplusplus
}
#endif
