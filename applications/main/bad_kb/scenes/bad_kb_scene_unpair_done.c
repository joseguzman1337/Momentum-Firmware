#include "../bad_kb_app_i.h"

static void bad_kb_scene_unpair_done_popup_callback(void* context) {
    BadKbApp* bad_kb = context;
    scene_manager_search_and_switch_to_previous_scene(bad_kb->scene_manager, BadKbSceneConfig);
}

void bad_kb_scene_unpair_done_on_enter(void* context) {
    BadKbApp* bad_kb = context;
    Popup* popup = bad_kb->popup;

    bad_kb_hid_ble_remove_pairing();

    popup_set_icon(popup, 48, 4, &I_DolphinDone_80x58);
    popup_set_header(popup, "Done", 20, 19, AlignLeft, AlignBottom);
    popup_set_callback(popup, bad_kb_scene_unpair_done_popup_callback);
    popup_set_context(popup, bad_kb);
    popup_set_timeout(popup, 1500);
    popup_enable_timeout(popup);

    view_dispatcher_switch_to_view(bad_kb->view_dispatcher, BadKbAppViewPopup);
}

bool bad_kb_scene_unpair_done_on_event(void* context, SceneManagerEvent event) {
    BadKbApp* bad_kb = context;
    UNUSED(bad_kb);
    UNUSED(event);
    bool consumed = false;

    return consumed;
}

void bad_kb_scene_unpair_done_on_exit(void* context) {
    BadKbApp* bad_kb = context;
    Popup* popup = bad_kb->popup;
    UNUSED(popup);

    popup_reset(popup);
}
