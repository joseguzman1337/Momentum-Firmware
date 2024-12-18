#include "../nfc_app_i.h"

enum SubmenuDebugIndex {
    SubmenuDebugIndexField,
    SubmenuDebugIndexApdu,
    SubmenuDebugIndexLogger,
};

void nfc_scene_debug_submenu_callback(void* context, uint32_t index) {
    NfcApp* nfc = context;

    view_dispatcher_send_custom_event(nfc->view_dispatcher, index);
}

void nfc_scene_debug_on_enter(void* context) {
    NfcApp* nfc = context;
    Submenu* submenu = nfc->submenu;

    submenu_add_item(
        submenu, "Field", SubmenuDebugIndexField, nfc_scene_debug_submenu_callback, nfc);

    submenu_add_item(
        submenu,
        nfc->logger_enabled ? "Disable Logger" : "Enable Logger",
        SubmenuDebugIndexLogger,
        nfc_scene_debug_submenu_callback,
        nfc);

    submenu_set_selected_item(
        submenu, scene_manager_get_scene_state(nfc->scene_manager, NfcSceneDebug));

    view_dispatcher_switch_to_view(nfc->view_dispatcher, NfcViewMenu);
}

bool nfc_scene_debug_on_event(void* context, SceneManagerEvent event) {
    NfcApp* nfc = context;
    bool consumed = false;

    if(event.type == SceneManagerEventTypeCustom) {
        if(event.event == SubmenuDebugIndexField) {
            scene_manager_set_scene_state(
                nfc->scene_manager, NfcSceneDebug, SubmenuDebugIndexField);
            scene_manager_next_scene(nfc->scene_manager, NfcSceneField);
            consumed = true;
        } else if(event.event == SubmenuDebugIndexLogger) {
            nfc->logger_enabled ^= 1;
            submenu_change_item_label(
                nfc->submenu,
                SubmenuDebugIndexLogger,
                nfc->logger_enabled ? "Disable Logger" : "Enable Logger");
            consumed = true;
        }
    }
    return consumed;
}

void nfc_scene_debug_on_exit(void* context) {
    NfcApp* nfc = context;

    submenu_reset(nfc->submenu);
}
