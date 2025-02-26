#include "../bad_kb_app_i.h"

enum ByteInputResult {
    ByteInputResultOk,
};

static void reverse_mac_addr(uint8_t mac_addr[GAP_MAC_ADDR_SIZE]) {
    uint8_t tmp;
    for(size_t i = 0; i < GAP_MAC_ADDR_SIZE / 2; i++) {
        tmp = mac_addr[i];
        mac_addr[i] = mac_addr[GAP_MAC_ADDR_SIZE - 1 - i];
        mac_addr[GAP_MAC_ADDR_SIZE - 1 - i] = tmp;
    }
}

void bad_kb_scene_config_ble_mac_byte_input_callback(void* context) {
    BadKbApp* bad_kb = context;

    view_dispatcher_send_custom_event(bad_kb->view_dispatcher, ByteInputResultOk);
}

void bad_kb_scene_config_ble_mac_on_enter(void* context) {
    BadKbApp* bad_kb = context;
    ByteInput* byte_input = bad_kb->byte_input;

    memcpy(bad_kb->ble_mac_buf, bad_kb->script_hid_cfg.ble.mac, sizeof(bad_kb->ble_mac_buf));
    reverse_mac_addr(bad_kb->ble_mac_buf);
    byte_input_set_header_text(byte_input, "Set BLE MAC address");

    byte_input_set_result_callback(
        byte_input,
        bad_kb_scene_config_ble_mac_byte_input_callback,
        NULL,
        bad_kb,
        bad_kb->ble_mac_buf,
        sizeof(bad_kb->ble_mac_buf));

    view_dispatcher_switch_to_view(bad_kb->view_dispatcher, BadKbAppViewByteInput);
}

bool bad_kb_scene_config_ble_mac_on_event(void* context, SceneManagerEvent event) {
    BadKbApp* bad_kb = context;
    bool consumed = false;

    if(event.type == SceneManagerEventTypeCustom) {
        consumed = true;
        if(event.event == ByteInputResultOk) {
            reverse_mac_addr(bad_kb->ble_mac_buf);
            // Apply to current script config
            memcpy(
                bad_kb->script_hid_cfg.ble.mac,
                bad_kb->ble_mac_buf,
                sizeof(bad_kb->script_hid_cfg.ble.mac));
            // Set in user config to save in settings file
            memcpy(
                bad_kb->user_hid_cfg.ble.mac,
                bad_kb->ble_mac_buf,
                sizeof(bad_kb->user_hid_cfg.ble.mac));
        }
        scene_manager_previous_scene(bad_kb->scene_manager);
    }
    return consumed;
}

void bad_kb_scene_config_ble_mac_on_exit(void* context) {
    BadKbApp* bad_kb = context;
    ByteInput* byte_input = bad_kb->byte_input;

    byte_input_set_result_callback(byte_input, NULL, NULL, NULL, NULL, 0);
    byte_input_set_header_text(byte_input, "");
}
