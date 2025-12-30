#include <furi.h>
#include <gui/gui.h>
#include <gui/view_dispatcher.h>
#include <gui/scene_manager.h>
#include <gui/modules/submenu.h>

#define TAG "{{APP_NAME}}"

typedef struct {
    ViewDispatcher* view_dispatcher;
    SceneManager* scene_manager;
    Submenu* submenu;
} {
    {
        APP_NAME
    }
}
App;

static {
    {
        APP_NAME
    }
}
App* {
    {
        APP_ID
    }
}
_app_alloc() {
    {
        {
            APP_NAME
        }
    }
    App* app = malloc(sizeof({
        {
            APP_NAME
        }
    } App));

    app->view_dispatcher = view_dispatcher_alloc();
    app->scene_manager = scene_manager_alloc(
        &{
            {
                APP_ID
            }
        } _scene_handlers,
        app);

    view_dispatcher_enable_queue(app->view_dispatcher);
    view_dispatcher_set_event_callback_context(app->view_dispatcher, app);

    app->submenu = submenu_alloc();
    view_dispatcher_add_view(app->view_dispatcher, 0, submenu_get_view(app->submenu));

    return app;
}

static void {
    {
        APP_ID
    }
}
_app_free({
    {
        APP_NAME
    }
} App* app) {
    furi_assert(app);

    view_dispatcher_remove_view(app->view_dispatcher, 0);
    submenu_free(app->submenu);

    scene_manager_free(app->scene_manager);
    view_dispatcher_free(app->view_dispatcher);

    free(app);
}

int32_t {
    {
        APP_ID
    }
}
_app(void* p) {
    UNUSED(p);

    {
        {
            APP_NAME
        }
    }
    App* app = { {APP_ID} } _app_alloc();

    Gui* gui = furi_record_open(RECORD_GUI);
    view_dispatcher_attach_to_gui(app->view_dispatcher, gui, ViewDispatcherTypeFullscreen);

    scene_manager_next_scene(app->scene_manager, 0);
    view_dispatcher_run(app->view_dispatcher);

    furi_record_close(RECORD_GUI);
    {
        {
            APP_ID
        }
    }
    _app_free(app);

    return 0;
}
