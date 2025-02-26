#include "../helpers/ducky_script.h"
#include "../bad_kb_app_i.h"
#include "../views/bad_kb_view.h"
#include <furi_hal.h>
#include "toolbox/path.h"

void bad_kb_scene_work_button_callback(InputKey key, void* context) {
    furi_assert(context);
    BadKbApp* app = context;
    view_dispatcher_send_custom_event(app->view_dispatcher, key);
}

bool bad_kb_scene_work_on_event(void* context, SceneManagerEvent event) {
    BadKbApp* app = context;
    bool consumed = false;

    if(event.type == SceneManagerEventTypeCustom) {
        if(event.event == InputKeyLeft) {
            if(bad_kb_view_is_idle_state(app->bad_kb_view)) {
                bad_kb_script_close(app->bad_kb_script);
                app->bad_kb_script = NULL;

                scene_manager_next_scene(app->scene_manager, BadKbSceneConfig);
            }
            consumed = true;
        } else if(event.event == InputKeyOk) {
            bad_kb_script_start_stop(app->bad_kb_script);
            consumed = true;
        } else if(event.event == InputKeyRight) {
            if(bad_kb_view_is_idle_state(app->bad_kb_view)) {
                bad_kb_set_interface(
                    app,
                    app->interface == BadKbHidInterfaceBle ? BadKbHidInterfaceUsb :
                                                             BadKbHidInterfaceBle);
                bad_kb_script_close(app->bad_kb_script);
                app->bad_kb_script = bad_kb_script_open(
                    app->file_path, &app->interface, &app->script_hid_cfg, false);
                bad_kb_script_set_keyboard_layout(app->bad_kb_script, app->keyboard_layout);
            } else {
                bad_kb_script_pause_resume(app->bad_kb_script);
            }
            consumed = true;
        }
    } else if(event.type == SceneManagerEventTypeTick) {
        bad_kb_view_set_state(app->bad_kb_view, bad_kb_script_get_state(app->bad_kb_script));
        bad_kb_view_set_interface(app->bad_kb_view, app->interface);
    }
    return consumed;
}

void bad_kb_scene_work_on_enter(void* context) {
    BadKbApp* app = context;

    bad_kb_view_set_interface(app->bad_kb_view, app->interface);

    // Opening script the first time:
    // - copy user settings as base config
    // - load ID/BLE_ID/BT_ID config if present
    // Then disable this until next script selected so user can customize options
    bool first_script_load = scene_manager_get_scene_state(app->scene_manager, BadKbSceneWork);
    if(first_script_load) {
        memcpy(&app->script_hid_cfg, &app->user_hid_cfg, sizeof(app->script_hid_cfg));
        scene_manager_set_scene_state(app->scene_manager, BadKbSceneWork, false);
    }
    // Interface and config are passed as pointers as ID/BLE_ID/BT_ID config can modify them
    app->bad_kb_script = bad_kb_script_open(
        app->file_path, &app->interface, &app->script_hid_cfg, first_script_load);
    bad_kb_script_set_keyboard_layout(app->bad_kb_script, app->keyboard_layout);

    FuriString* file_name;
    file_name = furi_string_alloc();
    path_extract_filename(app->file_path, file_name, true);
    bad_kb_view_set_file_name(app->bad_kb_view, furi_string_get_cstr(file_name));
    furi_string_free(file_name);

    FuriString* layout;
    layout = furi_string_alloc();
    path_extract_filename(app->keyboard_layout, layout, true);
    bad_kb_view_set_layout(app->bad_kb_view, furi_string_get_cstr(layout));
    furi_string_free(layout);

    bad_kb_view_set_state(app->bad_kb_view, bad_kb_script_get_state(app->bad_kb_script));

    bad_kb_view_set_button_callback(app->bad_kb_view, bad_kb_scene_work_button_callback, app);
    view_dispatcher_switch_to_view(app->view_dispatcher, BadKbAppViewWork);
}

void bad_kb_scene_work_on_exit(void* context) {
    UNUSED(context);
}
