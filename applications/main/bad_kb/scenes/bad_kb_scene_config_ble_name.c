#include "../bad_kb_app_i.h"

enum TextInputResult {
    TextInputResultOk,
};

static void bad_kb_scene_config_ble_name_text_input_callback(void* context) {
    BadKbApp* bad_kb = context;

    view_dispatcher_send_custom_event(bad_kb->view_dispatcher, TextInputResultOk);
}

void bad_kb_scene_config_ble_name_on_enter(void* context) {
    BadKbApp* bad_kb = context;
    TextInput* text_input = bad_kb->text_input;

    strlcpy(bad_kb->ble_name_buf, bad_kb->script_hid_cfg.ble.name, sizeof(bad_kb->ble_name_buf));
    text_input_set_header_text(text_input, "Set BLE device name");

    text_input_set_result_callback(
        text_input,
        bad_kb_scene_config_ble_name_text_input_callback,
        bad_kb,
        bad_kb->ble_name_buf,
        sizeof(bad_kb->ble_name_buf),
        true);

    view_dispatcher_switch_to_view(bad_kb->view_dispatcher, BadKbAppViewTextInput);
}

bool bad_kb_scene_config_ble_name_on_event(void* context, SceneManagerEvent event) {
    BadKbApp* bad_kb = context;
    bool consumed = false;

    if(event.type == SceneManagerEventTypeCustom) {
        consumed = true;
        if(event.event == TextInputResultOk) {
            // Apply to current script config
            strlcpy(
                bad_kb->script_hid_cfg.ble.name,
                bad_kb->ble_name_buf,
                sizeof(bad_kb->script_hid_cfg.ble.name));
            // Set in user config to save in settings file
            strlcpy(
                bad_kb->user_hid_cfg.ble.name,
                bad_kb->ble_name_buf,
                sizeof(bad_kb->user_hid_cfg.ble.name));
        }
        scene_manager_previous_scene(bad_kb->scene_manager);
    }
    return consumed;
}

void bad_kb_scene_config_ble_name_on_exit(void* context) {
    BadKbApp* bad_kb = context;
    TextInput* text_input = bad_kb->text_input;

    text_input_reset(text_input);
}
