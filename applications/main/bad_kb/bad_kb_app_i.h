#pragma once

#include "bad_kb_app.h"
#include "scenes/bad_kb_scene.h"
#include "helpers/ducky_script.h"
#include "helpers/bad_kb_hid.h"

#include <gui/gui.h>
#include <assets_icons.h>
#include <gui/view_dispatcher.h>
#include <gui/scene_manager.h>
#include <dialogs/dialogs.h>
#include <notification/notification_messages.h>
#include <gui/modules/variable_item_list.h>
#include <gui/modules/text_input.h>
#include <gui/modules/byte_input.h>
#include <gui/modules/loading.h>
#include <gui/modules/widget.h>
#include <gui/modules/popup.h>
#include "views/bad_kb_view.h"
#include <furi_hal_usb.h>

#define BAD_KB_APP_BASE_FOLDER        EXT_PATH("badusb")
#define BAD_KB_APP_PATH_LAYOUT_FOLDER BAD_KB_APP_BASE_FOLDER "/assets/layouts"
#define BAD_KB_APP_SCRIPT_EXTENSION   ".txt"
#define BAD_KB_APP_LAYOUT_EXTENSION   ".kl"

typedef enum {
    BadKbAppErrorNoFiles,
} BadKbAppError;

struct BadKbApp {
    Gui* gui;
    ViewDispatcher* view_dispatcher;
    SceneManager* scene_manager;
    NotificationApp* notifications;
    DialogsApp* dialogs;
    Widget* widget;
    Popup* popup;
    VariableItemList* var_item_list;
    TextInput* text_input;
    ByteInput* byte_input;
    Loading* loading;

    char ble_name_buf[FURI_HAL_BT_ADV_NAME_LENGTH];
    uint8_t ble_mac_buf[GAP_MAC_ADDR_SIZE];
    char usb_name_buf[HID_MANUF_PRODUCT_NAME_LEN];
    uint16_t usb_vidpid_buf[2];

    BadKbAppError error;
    FuriString* file_path;
    FuriString* keyboard_layout;
    BadKb* bad_kb_view;
    BadKbScript* bad_kb_script;

    BadKbHidInterface interface;
    BadKbHidConfig user_hid_cfg;
    BadKbHidConfig script_hid_cfg;
};

typedef enum {
    BadKbAppViewWidget,
    BadKbAppViewPopup,
    BadKbAppViewWork,
    BadKbAppViewConfig,
    BadKbAppViewByteInput,
    BadKbAppViewTextInput,
    BadKbAppViewLoading,
} BadKbAppView;

void bad_kb_set_interface(BadKbApp* app, BadKbHidInterface interface);

void bad_kb_app_show_loading_popup(BadKbApp* app, bool show);
