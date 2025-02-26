#include "../bad_kb_app_i.h"

enum ConfigIndex {
    ConfigIndexKeyboardLayout,
    ConfigIndexConnection,
};

enum ConfigIndexBle {
    ConfigIndexBleRemember = ConfigIndexConnection + 1,
    ConfigIndexBlePairing,
    ConfigIndexBleDeviceName,
    ConfigIndexBleMacAddress,
    ConfigIndexBleRandomizeMac,
    ConfigIndexBleUnpair,
};

enum ConfigIndexUsb {
    ConfigIndexUsbManufacturer = ConfigIndexConnection + 1,
    ConfigIndexUsbProductName,
    ConfigIndexUsbVidPid,
    ConfigIndexUsbRandomizeVidPid,
};

void bad_kb_scene_config_connection_callback(VariableItem* item) {
    BadKbApp* bad_kb = variable_item_get_context(item);
    bad_kb_set_interface(
        bad_kb,
        bad_kb->interface == BadKbHidInterfaceBle ? BadKbHidInterfaceUsb : BadKbHidInterfaceBle);
    variable_item_set_current_value_text(
        item, bad_kb->interface == BadKbHidInterfaceBle ? "BLE" : "USB");
    view_dispatcher_send_custom_event(bad_kb->view_dispatcher, ConfigIndexConnection);
}

void bad_kb_scene_config_ble_remember_callback(VariableItem* item) {
    BadKbApp* bad_kb = variable_item_get_context(item);
    bool value = variable_item_get_current_value_index(item);
    // Apply to current script config
    bad_kb->script_hid_cfg.ble.bonding = value;
    // Set in user config to save in settings file
    bad_kb->user_hid_cfg.ble.bonding = value;
    variable_item_set_current_value_text(item, value ? "ON" : "OFF");
}

const char* const ble_pairing_names[GapPairingCount] = {
    "YesNo",
    "PIN Type",
    "PIN Y/N",
};
void bad_kb_scene_config_ble_pairing_callback(VariableItem* item) {
    BadKbApp* bad_kb = variable_item_get_context(item);
    uint8_t index = variable_item_get_current_value_index(item);
    // Apply to current script config
    bad_kb->script_hid_cfg.ble.pairing = index;
    // Set in user config to save in settings file
    bad_kb->user_hid_cfg.ble.pairing = index;
    variable_item_set_current_value_text(item, ble_pairing_names[index]);
}

void bad_kb_scene_config_select_callback(void* context, uint32_t index) {
    BadKbApp* bad_kb = context;

    view_dispatcher_send_custom_event(bad_kb->view_dispatcher, index);
}

static void draw_menu(BadKbApp* bad_kb) {
    VariableItemList* var_item_list = bad_kb->var_item_list;
    VariableItem* item;

    variable_item_list_reset(var_item_list);

    variable_item_list_add(var_item_list, "Keyboard Layout (global)", 0, NULL, NULL);

    item = variable_item_list_add(
        var_item_list, "Connection", 2, bad_kb_scene_config_connection_callback, bad_kb);
    variable_item_set_current_value_index(item, bad_kb->interface == BadKbHidInterfaceBle);
    variable_item_set_current_value_text(
        item, bad_kb->interface == BadKbHidInterfaceBle ? "BLE" : "USB");

    if(bad_kb->interface == BadKbHidInterfaceBle) {
        BleProfileHidParams* ble_hid_cfg = &bad_kb->script_hid_cfg.ble;

        item = variable_item_list_add(
            var_item_list, "BLE Remember", 2, bad_kb_scene_config_ble_remember_callback, bad_kb);
        variable_item_set_current_value_index(item, ble_hid_cfg->bonding);
        variable_item_set_current_value_text(item, ble_hid_cfg->bonding ? "ON" : "OFF");

        item = variable_item_list_add(
            var_item_list,
            "BLE Pairing",
            GapPairingCount,
            bad_kb_scene_config_ble_pairing_callback,
            bad_kb);
        variable_item_set_current_value_index(item, ble_hid_cfg->pairing);
        variable_item_set_current_value_text(item, ble_pairing_names[ble_hid_cfg->pairing]);

        variable_item_list_add(var_item_list, "BLE Device Name", 0, NULL, NULL);

        variable_item_list_add(var_item_list, "BLE MAC Address", 0, NULL, NULL);

        variable_item_list_add(var_item_list, "Randomize BLE MAC", 0, NULL, NULL);

        variable_item_list_add(var_item_list, "Remove BLE Pairing", 0, NULL, NULL);
    } else {
        variable_item_list_add(var_item_list, "USB Manufacturer", 0, NULL, NULL);

        variable_item_list_add(var_item_list, "USB Product Name", 0, NULL, NULL);

        variable_item_list_add(var_item_list, "USB VID and PID", 0, NULL, NULL);

        variable_item_list_add(var_item_list, "Randomize USB VID:PID", 0, NULL, NULL);
    }
}

void bad_kb_scene_config_on_enter(void* context) {
    BadKbApp* bad_kb = context;
    VariableItemList* var_item_list = bad_kb->var_item_list;

    variable_item_list_set_enter_callback(
        var_item_list, bad_kb_scene_config_select_callback, bad_kb);
    draw_menu(bad_kb);
    variable_item_list_set_selected_item(
        var_item_list, scene_manager_get_scene_state(bad_kb->scene_manager, BadKbSceneConfig));

    view_dispatcher_switch_to_view(bad_kb->view_dispatcher, BadKbAppViewConfig);
}

bool bad_kb_scene_config_on_event(void* context, SceneManagerEvent event) {
    BadKbApp* bad_kb = context;
    bool consumed = false;

    if(event.type == SceneManagerEventTypeCustom) {
        scene_manager_set_scene_state(bad_kb->scene_manager, BadKbSceneConfig, event.event);
        consumed = true;
        switch(event.event) {
        case ConfigIndexKeyboardLayout:
            scene_manager_next_scene(bad_kb->scene_manager, BadKbSceneConfigLayout);
            break;
        case ConfigIndexConnection:
            // Refresh default values for new interface
            const BadKbHidApi* hid = bad_kb_hid_get_interface(bad_kb->interface);
            hid->adjust_config(&bad_kb->script_hid_cfg);
            // Redraw menu with new interface options
            draw_menu(bad_kb);
            break;
        default:
            break;
        }
        if(bad_kb->interface == BadKbHidInterfaceBle) {
            switch(event.event) {
            case ConfigIndexBleDeviceName:
                scene_manager_next_scene(bad_kb->scene_manager, BadKbSceneConfigBleName);
                break;
            case ConfigIndexBleMacAddress:
                scene_manager_next_scene(bad_kb->scene_manager, BadKbSceneConfigBleMac);
                break;
            case ConfigIndexBleRandomizeMac:
                // Apply to current script config
                furi_hal_random_fill_buf(
                    bad_kb->script_hid_cfg.ble.mac, sizeof(bad_kb->script_hid_cfg.ble.mac));
                // Set in user config to save in settings file
                memcpy(
                    bad_kb->user_hid_cfg.ble.mac,
                    bad_kb->script_hid_cfg.ble.mac,
                    sizeof(bad_kb->user_hid_cfg.ble.mac));
                break;
            case ConfigIndexBleUnpair:
                scene_manager_next_scene(bad_kb->scene_manager, BadKbSceneConfirmUnpair);
                break;
            default:
                break;
            }
        } else {
            switch(event.event) {
            case ConfigIndexUsbManufacturer:
                scene_manager_set_scene_state(
                    bad_kb->scene_manager, BadKbSceneConfigUsbName, true);
                scene_manager_next_scene(bad_kb->scene_manager, BadKbSceneConfigUsbName);
                break;
            case ConfigIndexUsbProductName:
                scene_manager_set_scene_state(
                    bad_kb->scene_manager, BadKbSceneConfigUsbName, false);
                scene_manager_next_scene(bad_kb->scene_manager, BadKbSceneConfigUsbName);
                break;
            case ConfigIndexUsbVidPid:
                scene_manager_next_scene(bad_kb->scene_manager, BadKbSceneConfigUsbVidPid);
                break;
            case ConfigIndexUsbRandomizeVidPid:
                furi_hal_random_fill_buf(
                    (void*)bad_kb->usb_vidpid_buf, sizeof(bad_kb->usb_vidpid_buf));
                // Apply to current script config
                bad_kb->script_hid_cfg.usb.vid = bad_kb->usb_vidpid_buf[0];
                bad_kb->script_hid_cfg.usb.pid = bad_kb->usb_vidpid_buf[1];
                // Set in user config to save in settings file
                bad_kb->user_hid_cfg.usb.vid = bad_kb->script_hid_cfg.usb.vid;
                bad_kb->user_hid_cfg.usb.pid = bad_kb->script_hid_cfg.usb.pid;
                break;
            default:
                break;
            }
        }
    }

    return consumed;
}

void bad_kb_scene_config_on_exit(void* context) {
    BadKbApp* bad_kb = context;
    VariableItemList* var_item_list = bad_kb->var_item_list;

    variable_item_list_reset(var_item_list);
}
