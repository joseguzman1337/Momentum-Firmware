#include "loading.h"

#include <gui/icon_animation.h>
#include <gui/elements.h>
#include <gui/canvas.h>
#include <gui/view.h>
#include <input/input.h>

#include <furi.h>
#include <assets_icons.h>
#include <stdint.h>

struct Loading {
    View* view;
};

typedef struct {
    IconAnimation* icon;
    uint8_t progress_width;
    bool progress_shown;
} LoadingModel;

#define LOADING_ICON_SIZE 24U
#define LOADING_BAR_WIDTH 64U
#define LOADING_BAR_GAP   4U
#define LOADING_BAR_BLOCK (LOADING_ICON_SIZE + LOADING_BAR_GAP + 9U)

static void loading_draw_callback(Canvas* canvas, void* _model) {
    LoadingModel* model = (LoadingModel*)_model;

    canvas_set_color(canvas, ColorWhite);
    canvas_draw_box(canvas, 0, 0, canvas_width(canvas), canvas_height(canvas));
    canvas_set_color(canvas, ColorBlack);

    const uint8_t x = canvas_width(canvas) / 2 - LOADING_ICON_SIZE / 2;
    const uint8_t block = model->progress_shown ? LOADING_BAR_BLOCK : LOADING_ICON_SIZE;
    const uint8_t y = canvas_height(canvas) / 2 - block / 2;

    canvas_draw_icon(canvas, x, y, &A_Loading_24);

    canvas_draw_icon_animation(canvas, x, y, model->icon);

    if(model->progress_shown) {
        const int32_t bar_x = canvas_width(canvas) / 2 - LOADING_BAR_WIDTH / 2;
        const int32_t bar_y = y + LOADING_ICON_SIZE + LOADING_BAR_GAP;
        canvas_set_color(canvas, ColorWhite);
        canvas_draw_box(canvas, bar_x + 1, bar_y + 1, LOADING_BAR_WIDTH - 2, 7);
        canvas_set_color(canvas, ColorBlack);
        canvas_draw_rframe(canvas, bar_x, bar_y, LOADING_BAR_WIDTH, 9, 3);
        canvas_draw_box(canvas, bar_x + 1, bar_y + 1, model->progress_width, 7);
    }
}

static bool loading_input_callback(InputEvent* event, void* context) {
    UNUSED(event);
    furi_assert(context);
    return true;
}

static void loading_enter_callback(void* context) {
    furi_assert(context);
    Loading* instance = context;
    LoadingModel* model = view_get_model(instance->view);
    /* using Loading View in conjunction with several
     * Stack View obligates to reassign
     * Update callback, as it can be rewritten
     */
    view_tie_icon_animation(instance->view, model->icon);
    icon_animation_start(model->icon);
    view_commit_model(instance->view, false);
}

static void loading_exit_callback(void* context) {
    furi_assert(context);
    Loading* instance = context;
    LoadingModel* model = view_get_model(instance->view);
    icon_animation_stop(model->icon);
    view_commit_model(instance->view, false);
}

Loading* loading_alloc(void) {
    Loading* instance = malloc(sizeof(Loading));
    instance->view = view_alloc();
    view_allocate_model(instance->view, ViewModelTypeLocking, sizeof(LoadingModel));
    LoadingModel* model = view_get_model(instance->view);
    model->icon = icon_animation_alloc(&A_Loading_24);
    model->progress_width = 0;
    model->progress_shown = false;
    view_tie_icon_animation(instance->view, model->icon);
    view_commit_model(instance->view, false);

    view_set_context(instance->view, instance);
    view_set_draw_callback(instance->view, loading_draw_callback);
    view_set_input_callback(instance->view, loading_input_callback);
    view_set_enter_callback(instance->view, loading_enter_callback);
    view_set_exit_callback(instance->view, loading_exit_callback);

    return instance;
}

void loading_free(Loading* instance) {
    furi_check(instance);

    LoadingModel* model = view_get_model(instance->view);
    icon_animation_free(model->icon);
    view_commit_model(instance->view, false);

    furi_assert(instance);
    view_free(instance->view);
    free(instance);
}

View* loading_get_view(Loading* instance) {
    furi_check(instance);
    return instance->view;
}

void loading_set_progress(Loading* instance, float progress) {
    furi_check(instance);
    const float clamped = CLAMP(progress, 1.0f, 0.0f);
    const uint8_t progress_width = (uint8_t)(clamped * (LOADING_BAR_WIDTH - 2) + 0.5f);
    bool changed;
    with_view_model(
        instance->view,
        LoadingModel * model,
        {
            changed = !model->progress_shown || model->progress_width != progress_width;
            model->progress_shown = true;
            model->progress_width = progress_width;
        },
        changed);
}

void loading_set_progress_ratio(Loading* instance, size_t completed, size_t total) {
    furi_check(instance);
    furi_check(total > 0);

    if(completed > total) completed = total;
    const size_t progress_width =
        ((completed * (LOADING_BAR_WIDTH - 2)) + (total / 2)) / total;
    bool changed;
    with_view_model(
        instance->view,
        LoadingModel * model,
        {
            changed = !model->progress_shown || model->progress_width != progress_width;
            model->progress_shown = true;
            model->progress_width = progress_width;
        },
        changed);
}

void loading_reset_progress(Loading* instance) {
    furi_check(instance);
    bool changed;
    with_view_model(
        instance->view,
        LoadingModel * model,
        {
            changed = model->progress_shown;
            model->progress_shown = false;
            model->progress_width = 0;
        },
        changed);
}
