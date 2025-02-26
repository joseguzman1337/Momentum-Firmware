#include "bad_kb_app_i.h"
#include <furi.h>
#include <furi_hal.h>
#include <storage/storage.h>
#include <lib/toolbox/path.h>
#include <flipper_format/flipper_format.h>

#define BAD_KB_SETTINGS_PATH           BAD_KB_APP_BASE_FOLDER "/.badkb.settings"
#define BAD_KB_SETTINGS_FILE_TYPE      "Flipper BadKB Settings File"
#define BAD_KB_SETTINGS_VERSION        1
#define BAD_KB_SETTINGS_DEFAULT_LAYOUT BAD_KB_APP_PATH_LAYOUT_FOLDER "/en-US.kl"

static bool bad_kb_app_custom_event_callback(void* context, uint32_t event) {
    furi_assert(context);
    BadKbApp* app = context;
    return scene_manager_handle_custom_event(app->scene_manager, event);
}

static bool bad_kb_app_back_event_callback(void* context) {
    furi_assert(context);
    BadKbApp* app = context;
    return scene_manager_handle_back_event(app->scene_manager);
}

static void bad_kb_app_tick_event_callback(void* context) {
    furi_assert(context);
    BadKbApp* app = context;
    scene_manager_handle_tick_event(app->scene_manager);
}

static void bad_kb_load_settings(BadKbApp* app) {
    Storage* storage = furi_record_open(RECORD_STORAGE);
    FlipperFormat* fff = flipper_format_file_alloc(storage);
    bool loaded = false;

    BadKbHidConfig* hid_cfg = &app->user_hid_cfg;
    FuriString* temp_str = furi_string_alloc();
    uint32_t temp_uint = 0;

    if(flipper_format_file_open_existing(fff, BAD_KB_SETTINGS_PATH)) {
        do {
            if(!flipper_format_read_header(fff, temp_str, &temp_uint)) break;
            if((strcmp(furi_string_get_cstr(temp_str), BAD_KB_SETTINGS_FILE_TYPE) != 0) ||
               (temp_uint != BAD_KB_SETTINGS_VERSION))
                break;

            if(flipper_format_read_string(fff, "layout", temp_str)) {
                furi_string_set(app->keyboard_layout, temp_str);
                FileInfo layout_file_info;
                FS_Error file_check_err = storage_common_stat(
                    storage, furi_string_get_cstr(app->keyboard_layout), &layout_file_info);
                if((file_check_err != FSE_OK) || (layout_file_info.size != 256)) {
                    furi_string_set(app->keyboard_layout, BAD_KB_SETTINGS_DEFAULT_LAYOUT);
                }
            } else {
                furi_string_set(app->keyboard_layout, BAD_KB_SETTINGS_DEFAULT_LAYOUT);
                flipper_format_rewind(fff);
            }

            if(!flipper_format_read_uint32(fff, "interface", &temp_uint, 1) ||
               temp_uint >= BadKbHidInterfaceMAX) {
                temp_uint = BadKbHidInterfaceUsb;
                flipper_format_rewind(fff);
            }
            app->interface = temp_uint;

            if(!flipper_format_read_bool(fff, "ble_bonding", &hid_cfg->ble.bonding, 1)) {
                hid_cfg->ble.bonding = true;
                flipper_format_rewind(fff);
            }

            if(!flipper_format_read_uint32(fff, "ble_pairing", &temp_uint, 1) ||
               temp_uint >= GapPairingCount) {
                temp_uint = GapPairingPinCodeVerifyYesNo;
                flipper_format_rewind(fff);
            }
            hid_cfg->ble.pairing = temp_uint;

            if(flipper_format_read_string(fff, "ble_name", temp_str)) {
                strlcpy(
                    hid_cfg->ble.name, furi_string_get_cstr(temp_str), sizeof(hid_cfg->ble.name));
            } else {
                hid_cfg->ble.name[0] = '\0';
                flipper_format_rewind(fff);
            }

            if(!flipper_format_read_hex(
                   fff, "ble_mac", hid_cfg->ble.mac, sizeof(hid_cfg->ble.mac))) {
                memset(hid_cfg->ble.mac, 0, sizeof(hid_cfg->ble.mac));
                flipper_format_rewind(fff);
            }

            if(flipper_format_read_string(fff, "usb_manuf", temp_str)) {
                strlcpy(
                    hid_cfg->usb.manuf,
                    furi_string_get_cstr(temp_str),
                    sizeof(hid_cfg->usb.manuf));
            } else {
                hid_cfg->usb.manuf[0] = '\0';
                flipper_format_rewind(fff);
            }

            if(flipper_format_read_string(fff, "usb_product", temp_str)) {
                strlcpy(
                    hid_cfg->usb.product,
                    furi_string_get_cstr(temp_str),
                    sizeof(hid_cfg->usb.product));
            } else {
                hid_cfg->usb.product[0] = '\0';
                flipper_format_rewind(fff);
            }

            if(!flipper_format_read_uint32(fff, "usb_vid", &hid_cfg->usb.vid, 1)) {
                hid_cfg->usb.vid = 0;
                flipper_format_rewind(fff);
            }

            if(!flipper_format_read_uint32(fff, "usb_pid", &hid_cfg->usb.pid, 1)) {
                hid_cfg->usb.pid = 0;
                flipper_format_rewind(fff);
            }

            loaded = true;
        } while(0);
    }

    furi_string_free(temp_str);

    flipper_format_free(fff);
    furi_record_close(RECORD_STORAGE);

    if(!loaded) {
        furi_string_set(app->keyboard_layout, BAD_KB_SETTINGS_DEFAULT_LAYOUT);
        app->interface = BadKbHidInterfaceUsb;
        hid_cfg->ble.bonding = true;
        hid_cfg->ble.pairing = GapPairingPinCodeVerifyYesNo;
        hid_cfg->ble.name[0] = '\0';
        memset(hid_cfg->ble.mac, 0, sizeof(hid_cfg->ble.mac));
        hid_cfg->usb.manuf[0] = '\0';
        hid_cfg->usb.product[0] = '\0';
        hid_cfg->usb.vid = 0;
        hid_cfg->usb.pid = 0;
    }
}

static void bad_kb_save_settings(BadKbApp* app) {
    Storage* storage = furi_record_open(RECORD_STORAGE);
    FlipperFormat* fff = flipper_format_file_alloc(storage);
    BadKbHidConfig* hid_cfg = &app->user_hid_cfg;
    uint32_t temp_uint = 0;

    if(flipper_format_file_open_always(fff, BAD_KB_SETTINGS_PATH)) {
        do {
            if(!flipper_format_write_header_cstr(
                   fff, BAD_KB_SETTINGS_FILE_TYPE, BAD_KB_SETTINGS_VERSION))
                break;
            if(!flipper_format_write_string(fff, "layout", app->keyboard_layout)) break;
            temp_uint = app->interface;
            if(!flipper_format_write_uint32(fff, "interface", &temp_uint, 1)) break;
            if(!flipper_format_write_bool(fff, "ble_bonding", &hid_cfg->ble.bonding, 1)) break;
            temp_uint = hid_cfg->ble.pairing;
            if(!flipper_format_write_uint32(fff, "ble_pairing", &temp_uint, 1)) break;
            if(!flipper_format_write_string_cstr(fff, "ble_name", hid_cfg->ble.name)) break;
            if(!flipper_format_write_hex(
                   fff, "ble_mac", (uint8_t*)&hid_cfg->ble.mac, sizeof(hid_cfg->ble.mac)))
                break;
            if(!flipper_format_write_string_cstr(fff, "usb_manuf", hid_cfg->usb.manuf)) break;
            if(!flipper_format_write_string_cstr(fff, "usb_product", hid_cfg->usb.product)) break;
            if(!flipper_format_write_uint32(fff, "usb_vid", &hid_cfg->usb.vid, 1)) break;
            if(!flipper_format_write_uint32(fff, "usb_pid", &hid_cfg->usb.pid, 1)) break;
        } while(0);
    }

    flipper_format_free(fff);
    furi_record_close(RECORD_STORAGE);
}

void bad_kb_set_interface(BadKbApp* app, BadKbHidInterface interface) {
    app->interface = interface;
    bad_kb_view_set_interface(app->bad_kb_view, interface);
}

void bad_kb_app_show_loading_popup(BadKbApp* app, bool show) {
    if(show) {
        // Raise timer priority so that animations can play
        furi_timer_set_thread_priority(FuriTimerThreadPriorityElevated);
        view_dispatcher_switch_to_view(app->view_dispatcher, BadKbAppViewLoading);
    } else {
        // Restore default timer priority
        furi_timer_set_thread_priority(FuriTimerThreadPriorityNormal);
    }
}

BadKbApp* bad_kb_app_alloc(char* arg) {
    BadKbApp* app = malloc(sizeof(BadKbApp));

    app->bad_kb_script = NULL;

    app->file_path = furi_string_alloc();
    app->keyboard_layout = furi_string_alloc();
    if(arg && strlen(arg)) {
        furi_string_set(app->file_path, arg);
    }

    bad_kb_load_settings(app);

    app->gui = furi_record_open(RECORD_GUI);
    app->notifications = furi_record_open(RECORD_NOTIFICATION);
    app->dialogs = furi_record_open(RECORD_DIALOGS);

    app->view_dispatcher = view_dispatcher_alloc();
    app->scene_manager = scene_manager_alloc(&bad_kb_scene_handlers, app);

    view_dispatcher_set_event_callback_context(app->view_dispatcher, app);
    view_dispatcher_set_tick_event_callback(
        app->view_dispatcher, bad_kb_app_tick_event_callback, 250);
    view_dispatcher_set_custom_event_callback(
        app->view_dispatcher, bad_kb_app_custom_event_callback);
    view_dispatcher_set_navigation_event_callback(
        app->view_dispatcher, bad_kb_app_back_event_callback);

    // Custom Widget
    app->widget = widget_alloc();
    view_dispatcher_add_view(
        app->view_dispatcher, BadKbAppViewWidget, widget_get_view(app->widget));

    // Popup
    app->popup = popup_alloc();
    view_dispatcher_add_view(app->view_dispatcher, BadKbAppViewPopup, popup_get_view(app->popup));

    app->var_item_list = variable_item_list_alloc();
    view_dispatcher_add_view(
        app->view_dispatcher, BadKbAppViewConfig, variable_item_list_get_view(app->var_item_list));

    app->bad_kb_view = bad_kb_view_alloc();
    view_dispatcher_add_view(
        app->view_dispatcher, BadKbAppViewWork, bad_kb_view_get_view(app->bad_kb_view));

    app->text_input = text_input_alloc();
    view_dispatcher_add_view(
        app->view_dispatcher, BadKbAppViewTextInput, text_input_get_view(app->text_input));

    app->byte_input = byte_input_alloc();
    view_dispatcher_add_view(
        app->view_dispatcher, BadKbAppViewByteInput, byte_input_get_view(app->byte_input));

    app->loading = loading_alloc();
    view_dispatcher_add_view(
        app->view_dispatcher, BadKbAppViewLoading, loading_get_view(app->loading));

    view_dispatcher_attach_to_gui(app->view_dispatcher, app->gui, ViewDispatcherTypeFullscreen);

    if(!furi_string_empty(app->file_path)) {
        scene_manager_set_scene_state(app->scene_manager, BadKbSceneWork, true);
        scene_manager_next_scene(app->scene_manager, BadKbSceneWork);
    } else {
        furi_string_set(app->file_path, BAD_KB_APP_BASE_FOLDER);
        scene_manager_next_scene(app->scene_manager, BadKbSceneFileSelect);
    }

    return app;
}

void bad_kb_app_free(BadKbApp* app) {
    furi_assert(app);

    if(app->bad_kb_script) {
        bad_kb_script_close(app->bad_kb_script);
        app->bad_kb_script = NULL;
    }

    // Views
    view_dispatcher_remove_view(app->view_dispatcher, BadKbAppViewWork);
    bad_kb_view_free(app->bad_kb_view);

    // Custom Widget
    view_dispatcher_remove_view(app->view_dispatcher, BadKbAppViewWidget);
    widget_free(app->widget);

    // Popup
    view_dispatcher_remove_view(app->view_dispatcher, BadKbAppViewPopup);
    popup_free(app->popup);

    // Config menu
    view_dispatcher_remove_view(app->view_dispatcher, BadKbAppViewConfig);
    variable_item_list_free(app->var_item_list);

    // Text Input
    view_dispatcher_remove_view(app->view_dispatcher, BadKbAppViewTextInput);
    text_input_free(app->text_input);

    // Byte Input
    view_dispatcher_remove_view(app->view_dispatcher, BadKbAppViewByteInput);
    byte_input_free(app->byte_input);

    // Loading
    view_dispatcher_remove_view(app->view_dispatcher, BadKbAppViewLoading);
    loading_free(app->loading);

    // View dispatcher
    view_dispatcher_free(app->view_dispatcher);
    scene_manager_free(app->scene_manager);

    // Close records
    furi_record_close(RECORD_GUI);
    furi_record_close(RECORD_NOTIFICATION);
    furi_record_close(RECORD_DIALOGS);

    bad_kb_save_settings(app);

    furi_string_free(app->file_path);
    furi_string_free(app->keyboard_layout);

    free(app);
}

int32_t bad_kb_app(void* p) {
    BadKbApp* bad_kb_app = bad_kb_app_alloc((char*)p);

    view_dispatcher_run(bad_kb_app->view_dispatcher);

    bad_kb_app_free(bad_kb_app);
    return 0;
}
