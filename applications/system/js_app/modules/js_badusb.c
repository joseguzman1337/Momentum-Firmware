#include <core/common_defines.h>
#include "../js_modules.h"
#include <furi_hal.h>
#include <strings.h>
#include <toolbox/hex.h>
#include "../../main/bad_usb/helpers/bad_usb_hid.h"

#define ASCII_TO_KEY(layout, x) (((uint8_t)x < 128) ? (layout[(uint8_t)x]) : HID_KEYBOARD_NONE)

typedef struct {
    uint16_t layout[128];
    BadUsbHidConfig* hid_cfg;
    const BadUsbHidApi* hid_api;
    void* hid_inst;
    BadUsbHidInterface interface;
    uint8_t key_hold_cnt;
    bool started;
} JsBadusbInst;

static const struct {
    char* name;
    uint16_t code;
} key_codes[] = {
    {"CTRL", KEY_MOD_LEFT_CTRL},
    {"SHIFT", KEY_MOD_LEFT_SHIFT},
    {"ALT", KEY_MOD_LEFT_ALT},
    {"GUI", KEY_MOD_LEFT_GUI},

    {"DOWN", HID_KEYBOARD_DOWN_ARROW},
    {"LEFT", HID_KEYBOARD_LEFT_ARROW},
    {"RIGHT", HID_KEYBOARD_RIGHT_ARROW},
    {"UP", HID_KEYBOARD_UP_ARROW},

    {"ENTER", HID_KEYBOARD_RETURN},
    {"PAUSE", HID_KEYBOARD_PAUSE},
    {"CAPSLOCK", HID_KEYBOARD_CAPS_LOCK},
    {"DELETE", HID_KEYBOARD_DELETE_FORWARD},
    {"BACKSPACE", HID_KEYBOARD_DELETE},
    {"END", HID_KEYBOARD_END},
    {"ESC", HID_KEYBOARD_ESCAPE},
    {"HOME", HID_KEYBOARD_HOME},
    {"INSERT", HID_KEYBOARD_INSERT},
    {"NUMLOCK", HID_KEYPAD_NUMLOCK},
    {"PAGEUP", HID_KEYBOARD_PAGE_UP},
    {"PAGEDOWN", HID_KEYBOARD_PAGE_DOWN},
    {"PRINTSCREEN", HID_KEYBOARD_PRINT_SCREEN},
    {"SCROLLLOCK", HID_KEYBOARD_SCROLL_LOCK},
    {"SPACE", HID_KEYBOARD_SPACEBAR},
    {"TAB", HID_KEYBOARD_TAB},
    {"MENU", HID_KEYBOARD_APPLICATION},

    {"F1", HID_KEYBOARD_F1},
    {"F2", HID_KEYBOARD_F2},
    {"F3", HID_KEYBOARD_F3},
    {"F4", HID_KEYBOARD_F4},
    {"F5", HID_KEYBOARD_F5},
    {"F6", HID_KEYBOARD_F6},
    {"F7", HID_KEYBOARD_F7},
    {"F8", HID_KEYBOARD_F8},
    {"F9", HID_KEYBOARD_F9},
    {"F10", HID_KEYBOARD_F10},
    {"F11", HID_KEYBOARD_F11},
    {"F12", HID_KEYBOARD_F12},
    {"F13", HID_KEYBOARD_F13},
    {"F14", HID_KEYBOARD_F14},
    {"F15", HID_KEYBOARD_F15},
    {"F16", HID_KEYBOARD_F16},
    {"F17", HID_KEYBOARD_F17},
    {"F18", HID_KEYBOARD_F18},
    {"F19", HID_KEYBOARD_F19},
    {"F20", HID_KEYBOARD_F20},
    {"F21", HID_KEYBOARD_F21},
    {"F22", HID_KEYBOARD_F22},
    {"F23", HID_KEYBOARD_F23},
    {"F24", HID_KEYBOARD_F24},

    {"NUM0", HID_KEYPAD_0},
    {"NUM1", HID_KEYPAD_1},
    {"NUM2", HID_KEYPAD_2},
    {"NUM3", HID_KEYPAD_3},
    {"NUM4", HID_KEYPAD_4},
    {"NUM5", HID_KEYPAD_5},
    {"NUM6", HID_KEYPAD_6},
    {"NUM7", HID_KEYPAD_7},
    {"NUM8", HID_KEYPAD_8},
    {"NUM9", HID_KEYPAD_9},
};

static void js_badusb_quit_free(JsBadusbInst* badusb) {
    if(badusb->started) {
        badusb->hid_api->release_all(badusb->hid_inst);
        badusb->hid_api->deinit(badusb->hid_inst);
        badusb->hid_inst = NULL;
        badusb->hid_api = NULL;
        badusb->started = false;
        badusb->key_hold_cnt = 0;
    }
    if(badusb->hid_cfg) {
        free(badusb->hid_cfg);
        badusb->hid_cfg = NULL;
    }
}

static void js_badusb_reset_layout(JsBadusbInst* badusb) {
    memcpy(badusb->layout, hid_asciimap, MIN(sizeof(hid_asciimap), sizeof(badusb->layout)));
}

static bool setup_parse_layout_path(
    JsBadusbInst* badusb,
    struct mjs* mjs,
    mjs_val_t layout_obj) {
    if(mjs_is_string(layout_obj)) {
        size_t str_len = 0;
        const char* str_temp = mjs_get_string(mjs, &layout_obj, &str_len);
        if((str_len == 0) || (str_temp == NULL)) {
            return false;
        }
        File* file = storage_file_alloc(furi_record_open(RECORD_STORAGE));
        bool layout_loaded = storage_file_open(file, str_temp, FSAM_READ, FSOM_OPEN_EXISTING) &&
                             storage_file_read(file, badusb->layout, sizeof(badusb->layout)) ==
                                 sizeof(badusb->layout);
        storage_file_free(file);
        furi_record_close(RECORD_STORAGE);
        return layout_loaded;
    }
    return true;
}

static bool setup_parse_params_usb(
    JsBadusbInst* badusb,
    struct mjs* mjs,
    mjs_val_t arg,
    BadUsbHidConfig* hid_cfg) {
    if(!mjs_is_object(arg)) {
        return false;
    }
    mjs_val_t vid_obj = mjs_get(mjs, arg, "vid", ~0);
    mjs_val_t pid_obj = mjs_get(mjs, arg, "pid", ~0);
    mjs_val_t mfr_obj = mjs_get(mjs, arg, "mfrName", ~0);
    mjs_val_t prod_obj = mjs_get(mjs, arg, "prodName", ~0);
    mjs_val_t layout_obj = mjs_get(mjs, arg, "layoutPath", ~0);

    if(mjs_is_number(vid_obj) && mjs_is_number(pid_obj)) {
        hid_cfg->usb.vid = mjs_get_int32(mjs, vid_obj);
        hid_cfg->usb.pid = mjs_get_int32(mjs, pid_obj);
    } else {
        return false;
    }

    if(mjs_is_string(mfr_obj)) {
        size_t str_len = 0;
        const char* str_temp = mjs_get_string(mjs, &mfr_obj, &str_len);
        if((str_len == 0) || (str_temp == NULL)) {
            return false;
        }
        strlcpy(hid_cfg->usb.manuf, str_temp, sizeof(hid_cfg->usb.manuf));
    }

    if(mjs_is_string(prod_obj)) {
        size_t str_len = 0;
        const char* str_temp = mjs_get_string(mjs, &prod_obj, &str_len);
        if((str_len == 0) || (str_temp == NULL)) {
            return false;
        }
        strlcpy(hid_cfg->usb.product, str_temp, sizeof(hid_cfg->usb.product));
    }

    if(!setup_parse_layout_path(badusb, mjs, layout_obj)) {
        return false;
    }

    return true;
}

static void reverse_mac_addr(uint8_t mac_addr[GAP_MAC_ADDR_SIZE]) {
    uint8_t tmp = 0;
    for(size_t i = 0; i < GAP_MAC_ADDR_SIZE / 2; i++) {
        tmp = mac_addr[i];
        mac_addr[i] = mac_addr[GAP_MAC_ADDR_SIZE - 1 - i];
        mac_addr[GAP_MAC_ADDR_SIZE - 1 - i] = tmp;
    }
}

static bool parse_hex_mac_string(const char* text, size_t text_len, uint8_t out[GAP_MAC_ADDR_SIZE]) {
    char hex_buf[GAP_MAC_ADDR_SIZE * 2];
    size_t hex_len = 0;

    for(size_t i = 0; i < text_len; i++) {
        char c = text[i];
        bool is_hex = ((c >= '0' && c <= '9') || (c >= 'a' && c <= 'f') ||
                       (c >= 'A' && c <= 'F'));
        if(is_hex) {
            if(hex_len >= sizeof(hex_buf)) {
                return false;
            }
            hex_buf[hex_len++] = c;
        } else if(c == ':' || c == '-' || c == ' ' || c == '.') {
            continue;
        } else {
            return false;
        }
    }

    if(hex_len != sizeof(hex_buf)) {
        return false;
    }

    for(size_t i = 0; i < GAP_MAC_ADDR_SIZE; i++) {
        if(!hex_char_to_uint8(hex_buf[i * 2], hex_buf[i * 2 + 1], &out[i])) {
            return false;
        }
    }

    return true;
}

static bool parse_ble_mac(
    struct mjs* mjs,
    mjs_val_t mac_obj,
    uint8_t out[GAP_MAC_ADDR_SIZE]) {
    if(mjs_is_string(mac_obj)) {
        size_t str_len = 0;
        const char* str_temp = mjs_get_string(mjs, &mac_obj, &str_len);
        if((str_len == 0) || (str_temp == NULL)) {
            return false;
        }
        if(!parse_hex_mac_string(str_temp, str_len, out)) {
            return false;
        }
        reverse_mac_addr(out);
        return true;
    }

    if(mjs_is_typed_array(mac_obj)) {
        if(mjs_is_data_view(mac_obj)) {
            mac_obj = mjs_dataview_get_buf(mjs, mac_obj);
        }
        size_t mac_len = 0;
        char* mac_ptr = mjs_array_buf_get_ptr(mjs, mac_obj, &mac_len);
        if(!mac_ptr || mac_len != GAP_MAC_ADDR_SIZE) {
            return false;
        }
        memcpy(out, mac_ptr, GAP_MAC_ADDR_SIZE);
        reverse_mac_addr(out);
        return true;
    }

    return false;
}

static bool parse_pairing_value(struct mjs* mjs, mjs_val_t pairing_obj, GapPairing* pairing) {
    if(mjs_is_number(pairing_obj)) {
        int32_t pairing_val = mjs_get_int32(mjs, pairing_obj);
        if(pairing_val < 0 || pairing_val >= (int32_t)GapPairingCount) {
            return false;
        }
        *pairing = (GapPairing)pairing_val;
        return true;
    }

    if(mjs_is_string(pairing_obj)) {
        size_t str_len = 0;
        const char* str_temp = mjs_get_string(mjs, &pairing_obj, &str_len);
        if((str_len == 0) || (str_temp == NULL)) {
            return false;
        }
        if(strcasecmp(str_temp, "YesNo") == 0 || strcasecmp(str_temp, "None") == 0) {
            *pairing = GapPairingNone;
            return true;
        }
        if(strcasecmp(str_temp, "PinType") == 0 || strcasecmp(str_temp, "PinCode") == 0 ||
           strcasecmp(str_temp, "Pin") == 0) {
            *pairing = GapPairingPinCodeShow;
            return true;
        }
        if(strcasecmp(str_temp, "PinYesNo") == 0 || strcasecmp(str_temp, "PinYN") == 0 ||
           strcasecmp(str_temp, "PinCodeYesNo") == 0 || strcasecmp(str_temp, "PinY/N") == 0) {
            *pairing = GapPairingPinCodeVerifyYesNo;
            return true;
        }
    }

    return false;
}

static bool setup_parse_params_ble(
    JsBadusbInst* badusb,
    struct mjs* mjs,
    mjs_val_t arg,
    BadUsbHidConfig* hid_cfg) {
    if(!mjs_is_object(arg)) {
        return false;
    }

    mjs_val_t name_obj = mjs_get(mjs, arg, "name", ~0);
    mjs_val_t mac_obj = mjs_get(mjs, arg, "mac", ~0);
    mjs_val_t bonding_obj = mjs_get(mjs, arg, "bonding", ~0);
    mjs_val_t pairing_obj = mjs_get(mjs, arg, "pairing", ~0);
    mjs_val_t layout_obj = mjs_get(mjs, arg, "layoutPath", ~0);

    if(!mjs_is_undefined(name_obj)) {
        if(!mjs_is_string(name_obj)) {
            return false;
        }
        size_t str_len = 0;
        const char* str_temp = mjs_get_string(mjs, &name_obj, &str_len);
        if(str_temp == NULL) {
            return false;
        }
        strlcpy(hid_cfg->ble.name, str_temp, sizeof(hid_cfg->ble.name));
    }

    if(!mjs_is_undefined(mac_obj)) {
        if(!parse_ble_mac(mjs, mac_obj, hid_cfg->ble.mac)) {
            return false;
        }
    }

    if(!mjs_is_undefined(bonding_obj)) {
        if(mjs_is_boolean(bonding_obj)) {
            hid_cfg->ble.bonding = mjs_get_bool(mjs, bonding_obj);
        } else if(mjs_is_number(bonding_obj)) {
            hid_cfg->ble.bonding = mjs_get_int32(mjs, bonding_obj) != 0;
        } else {
            return false;
        }
    }

    if(!mjs_is_undefined(pairing_obj)) {
        GapPairing pairing = hid_cfg->ble.pairing;
        if(!parse_pairing_value(mjs, pairing_obj, &pairing)) {
            return false;
        }
        hid_cfg->ble.pairing = pairing;
    }

    if(!setup_parse_layout_path(badusb, mjs, layout_obj)) {
        return false;
    }

    return true;
}

static void js_badusb_setup_internal(
    struct mjs* mjs,
    JsBadusbInst* badusb,
    BadUsbHidInterface interface) {
    if(badusb->started) {
        mjs_prepend_errorf(mjs, MJS_INTERNAL_ERROR, "HID is already started");
        mjs_return(mjs, MJS_UNDEFINED);
        return;
    }

    bool args_correct = false;
    size_t num_args = mjs_nargs(mjs);

    badusb->hid_cfg = malloc(sizeof(BadUsbHidConfig));
    if(!badusb->hid_cfg) {
        mjs_prepend_errorf(mjs, MJS_INTERNAL_ERROR, "Out of memory");
        mjs_return(mjs, MJS_UNDEFINED);
        return;
    }
    memset(badusb->hid_cfg, 0, sizeof(BadUsbHidConfig));
    js_badusb_reset_layout(badusb);

    if(interface == BadUsbHidInterfaceBle) {
        badusb->hid_cfg->ble.bonding = true;
        badusb->hid_cfg->ble.pairing = GapPairingPinCodeVerifyYesNo;
    }

    if(num_args == 0) {
        args_correct = true;
    } else if(num_args == 1) {
        if(interface == BadUsbHidInterfaceUsb) {
            args_correct = setup_parse_params_usb(badusb, mjs, mjs_arg(mjs, 0), badusb->hid_cfg);
        } else {
            args_correct = setup_parse_params_ble(badusb, mjs, mjs_arg(mjs, 0), badusb->hid_cfg);
        }
    }

    if(!args_correct) {
        js_badusb_quit_free(badusb);
        mjs_prepend_errorf(mjs, MJS_BAD_ARGS_ERROR, "");
        mjs_return(mjs, MJS_UNDEFINED);
        return;
    }

    badusb->hid_api = bad_usb_hid_get_interface(interface);
    badusb->hid_api->adjust_config(badusb->hid_cfg);
    badusb->hid_inst = badusb->hid_api->init(badusb->hid_cfg);
    badusb->interface = interface;
    badusb->started = true;
    badusb->key_hold_cnt = 0;

    mjs_return(mjs, MJS_UNDEFINED);
}

static void js_badusb_setup(struct mjs* mjs) {
    mjs_val_t obj_inst = mjs_get(mjs, mjs_get_this(mjs), INST_PROP_NAME, ~0);
    JsBadusbInst* badusb = mjs_get_ptr(mjs, obj_inst);
    furi_assert(badusb);

    js_badusb_setup_internal(mjs, badusb, BadUsbHidInterfaceUsb);
}

static void js_badusb_setup_ble(struct mjs* mjs) {
    mjs_val_t obj_inst = mjs_get(mjs, mjs_get_this(mjs), INST_PROP_NAME, ~0);
    JsBadusbInst* badusb = mjs_get_ptr(mjs, obj_inst);
    furi_assert(badusb);

    js_badusb_setup_internal(mjs, badusb, BadUsbHidInterfaceBle);
}

static void js_badusb_quit(struct mjs* mjs) {
    mjs_val_t obj_inst = mjs_get(mjs, mjs_get_this(mjs), INST_PROP_NAME, ~0);
    JsBadusbInst* badusb = mjs_get_ptr(mjs, obj_inst);
    furi_assert(badusb);

    if(!badusb->started) {
        mjs_prepend_errorf(mjs, MJS_INTERNAL_ERROR, "HID is not started");
        mjs_return(mjs, MJS_UNDEFINED);
        return;
    }

    js_badusb_quit_free(badusb);

    mjs_return(mjs, MJS_UNDEFINED);
}

static void js_badusb_is_connected(struct mjs* mjs) {
    mjs_val_t obj_inst = mjs_get(mjs, mjs_get_this(mjs), INST_PROP_NAME, ~0);
    JsBadusbInst* badusb = mjs_get_ptr(mjs, obj_inst);
    furi_assert(badusb);

    if(!badusb->started) {
        mjs_prepend_errorf(mjs, MJS_INTERNAL_ERROR, "HID is not started");
        mjs_return(mjs, MJS_UNDEFINED);
        return;
    }

    bool is_connected = badusb->hid_api->is_connected(badusb->hid_inst);
    mjs_return(mjs, mjs_mk_boolean(mjs, is_connected));
}

static void js_badusb_get_lock_state(struct mjs* mjs) {
    mjs_val_t obj_inst = mjs_get(mjs, mjs_get_this(mjs), INST_PROP_NAME, ~0);
    JsBadusbInst* badusb = mjs_get_ptr(mjs, obj_inst);
    furi_assert(badusb);

    if(!badusb->started) {
        mjs_prepend_errorf(mjs, MJS_INTERNAL_ERROR, "HID is not started");
        mjs_return(mjs, MJS_UNDEFINED);
        return;
    }

    uint8_t leds = badusb->hid_api->get_led_state(badusb->hid_inst);
    mjs_val_t obj = mjs_mk_object(mjs);
    mjs_set(mjs, obj, "caps", ~0, mjs_mk_boolean(mjs, (leds & HID_KB_LED_CAPS) != 0));
    mjs_set(mjs, obj, "num", ~0, mjs_mk_boolean(mjs, (leds & HID_KB_LED_NUM) != 0));
    mjs_set(
        mjs,
        obj,
        "scroll",
        ~0,
        mjs_mk_boolean(mjs, (leds & HID_KB_LED_SCROLL) != 0));

    mjs_return(mjs, obj);
}

uint16_t get_keycode_by_name(JsBadusbInst* badusb, const char* key_name, size_t name_len) {
    if(name_len == 1) { // Single char
        return (ASCII_TO_KEY(badusb->layout, key_name[0]));
    }

    for(size_t i = 0; i < COUNT_OF(key_codes); i++) {
        size_t key_cmd_len = strlen(key_codes[i].name);
        if(key_cmd_len != name_len) {
            continue;
        }

        if(strncmp(key_name, key_codes[i].name, name_len) == 0) {
            return key_codes[i].code;
        }
    }

    return HID_KEYBOARD_NONE;
}

static bool parse_keycode(JsBadusbInst* badusb, struct mjs* mjs, size_t nargs, uint16_t* keycode) {
    uint16_t key_tmp = 0;
    for(size_t i = 0; i < nargs; i++) {
        mjs_val_t arg = mjs_arg(mjs, i);
        if(mjs_is_string(arg)) {
            size_t name_len = 0;
            const char* key_name = mjs_get_string(mjs, &arg, &name_len);
            if((key_name == NULL) || (name_len == 0)) {
                // String error
                return false;
            }
            uint16_t str_key = get_keycode_by_name(badusb, key_name, name_len);
            if(str_key == HID_KEYBOARD_NONE) {
                // Unknown key code
                return false;
            }
            if((str_key & 0xFF) && (key_tmp & 0xFF)) {
                // Main key is already defined
                return false;
            }
            key_tmp |= str_key;
        } else if(mjs_is_number(arg)) {
            uint32_t keycode_number = (uint32_t)mjs_get_int32(mjs, arg);
            if(((key_tmp & 0xFF) != 0) || (keycode_number > 0xFF)) {
                return false;
            }
            key_tmp |= keycode_number & 0xFF;
        } else {
            return false;
        }
    }
    *keycode = key_tmp;
    return true;
}

static void js_badusb_press(struct mjs* mjs) {
    mjs_val_t obj_inst = mjs_get(mjs, mjs_get_this(mjs), INST_PROP_NAME, ~0);
    JsBadusbInst* badusb = mjs_get_ptr(mjs, obj_inst);
    furi_assert(badusb);
    if(!badusb->started) {
        mjs_prepend_errorf(mjs, MJS_INTERNAL_ERROR, "HID is not started");
        mjs_return(mjs, MJS_UNDEFINED);
        return;
    }

    bool args_correct = false;
    uint16_t keycode = HID_KEYBOARD_NONE;
    size_t num_args = mjs_nargs(mjs);
    if(num_args > 0) {
        args_correct = parse_keycode(badusb, mjs, num_args, &keycode);
    }
    if(!args_correct) {
        mjs_prepend_errorf(mjs, MJS_BAD_ARGS_ERROR, "");
        mjs_return(mjs, MJS_UNDEFINED);
        return;
    }
    badusb->hid_api->kb_press(badusb->hid_inst, keycode);
    badusb->hid_api->kb_release(badusb->hid_inst, keycode);
    mjs_return(mjs, MJS_UNDEFINED);
}

static void js_badusb_hold(struct mjs* mjs) {
    mjs_val_t obj_inst = mjs_get(mjs, mjs_get_this(mjs), INST_PROP_NAME, ~0);
    JsBadusbInst* badusb = mjs_get_ptr(mjs, obj_inst);
    furi_assert(badusb);
    if(!badusb->started) {
        mjs_prepend_errorf(mjs, MJS_INTERNAL_ERROR, "HID is not started");
        mjs_return(mjs, MJS_UNDEFINED);
        return;
    }

    bool args_correct = false;
    uint16_t keycode = HID_KEYBOARD_NONE;
    size_t num_args = mjs_nargs(mjs);
    if(num_args > 0) {
        args_correct = parse_keycode(badusb, mjs, num_args, &keycode);
    }
    if(!args_correct) {
        mjs_prepend_errorf(mjs, MJS_BAD_ARGS_ERROR, "");
        mjs_return(mjs, MJS_UNDEFINED);
        return;
    }
    if(keycode & 0xFF) {
        badusb->key_hold_cnt++;
        if(badusb->key_hold_cnt > (HID_KB_MAX_KEYS - 1)) {
            mjs_prepend_errorf(mjs, MJS_INTERNAL_ERROR, "Too many keys are hold");
            badusb->hid_api->release_all(badusb->hid_inst);
            mjs_return(mjs, MJS_UNDEFINED);
            return;
        }
    }
    badusb->hid_api->kb_press(badusb->hid_inst, keycode);
    mjs_return(mjs, MJS_UNDEFINED);
}

static void js_badusb_release(struct mjs* mjs) {
    mjs_val_t obj_inst = mjs_get(mjs, mjs_get_this(mjs), INST_PROP_NAME, ~0);
    JsBadusbInst* badusb = mjs_get_ptr(mjs, obj_inst);
    furi_assert(badusb);
    if(!badusb->started) {
        mjs_prepend_errorf(mjs, MJS_INTERNAL_ERROR, "HID is not started");
        mjs_return(mjs, MJS_UNDEFINED);
        return;
    }

    bool args_correct = false;
    uint16_t keycode = HID_KEYBOARD_NONE;
    size_t num_args = mjs_nargs(mjs);
    if(num_args == 0) {
        badusb->hid_api->release_all(badusb->hid_inst);
        badusb->key_hold_cnt = 0;
        mjs_return(mjs, MJS_UNDEFINED);
        return;
    } else {
        args_correct = parse_keycode(badusb, mjs, num_args, &keycode);
    }
    if(!args_correct) {
        mjs_prepend_errorf(mjs, MJS_BAD_ARGS_ERROR, "");
        mjs_return(mjs, MJS_UNDEFINED);
        return;
    }
    if((keycode & 0xFF) && (badusb->key_hold_cnt > 0)) {
        badusb->key_hold_cnt--;
    }
    badusb->hid_api->kb_release(badusb->hid_inst, keycode);
    mjs_return(mjs, MJS_UNDEFINED);
}

// Make sure NUMLOCK is enabled for altchar
static void ducky_numlock_on(JsBadusbInst* badusb) {
    if((badusb->hid_api->get_led_state(badusb->hid_inst) & HID_KB_LED_NUM) == 0) {
        badusb->hid_api->kb_press(badusb->hid_inst, HID_KEYBOARD_LOCK_NUM_LOCK);
        badusb->hid_api->kb_release(badusb->hid_inst, HID_KEYBOARD_LOCK_NUM_LOCK);
    }
}

// Simulate pressing a character using ALT+Numpad ASCII code
static void ducky_altchar(JsBadusbInst* badusb, const char* ascii_code) {
    // Hold the ALT key
    badusb->hid_api->kb_press(badusb->hid_inst, KEY_MOD_LEFT_ALT);

    // Press the corresponding numpad key for each digit of the ASCII code
    for(size_t i = 0; ascii_code[i] != '\0'; i++) {
        char digitChar[5] = {'N', 'U', 'M', ascii_code[i], '\0'}; // Construct the numpad key name
        uint16_t numpad_keycode = get_keycode_by_name(badusb, digitChar, strlen(digitChar));
        if(numpad_keycode == HID_KEYBOARD_NONE) {
            continue; // Skip if keycode not found
        }
        badusb->hid_api->kb_press(badusb->hid_inst, numpad_keycode);
        badusb->hid_api->kb_release(badusb->hid_inst, numpad_keycode);
    }

    // Release the ALT key
    badusb->hid_api->kb_release(badusb->hid_inst, KEY_MOD_LEFT_ALT);
}

static void badusb_print(struct mjs* mjs, bool ln, bool alt) {
    mjs_val_t obj_inst = mjs_get(mjs, mjs_get_this(mjs), INST_PROP_NAME, ~0);
    JsBadusbInst* badusb = mjs_get_ptr(mjs, obj_inst);
    furi_assert(badusb);
    if(!badusb->started) {
        mjs_prepend_errorf(mjs, MJS_INTERNAL_ERROR, "HID is not started");
        mjs_return(mjs, MJS_UNDEFINED);
        return;
    }
    bool args_correct = false;
    const char* text_str = NULL;
    size_t text_len = 0;
    uint32_t delay_val = 0;
    do {
        mjs_val_t obj_string = MJS_UNDEFINED;
        size_t num_args = mjs_nargs(mjs);
        if(num_args == 1) {
            obj_string = mjs_arg(mjs, 0);
        } else if(num_args == 2) {
            obj_string = mjs_arg(mjs, 0);
            mjs_val_t obj_delay = mjs_arg(mjs, 1);
            if(!mjs_is_number(obj_delay)) {
                break;
            }
            delay_val = (uint32_t)mjs_get_int32(mjs, obj_delay);
            if(delay_val > 60000) {
                break;
            }
        }

        if(!mjs_is_string(obj_string)) {
            break;
        }
        text_str = mjs_get_string(mjs, &obj_string, &text_len);
        if((text_str == NULL) || (text_len == 0)) {
            break;
        }
        args_correct = true;
    } while(0);

    if(!args_correct) {
        mjs_prepend_errorf(mjs, MJS_BAD_ARGS_ERROR, "");
        mjs_return(mjs, MJS_UNDEFINED);
        return;
    }

    if(alt) {
        ducky_numlock_on(badusb);
    }
    for(size_t i = 0; i < text_len; i++) {
        if(alt) {
            // Convert character to ascii numeric value
            char ascii_str[4];
            snprintf(ascii_str, sizeof(ascii_str), "%u", (uint8_t)text_str[i]);
            ducky_altchar(badusb, ascii_str);
        } else {
            uint16_t keycode = ASCII_TO_KEY(badusb->layout, text_str[i]);
            badusb->hid_api->kb_press(badusb->hid_inst, keycode);
            badusb->hid_api->kb_release(badusb->hid_inst, keycode);
        }
        if(delay_val > 0) {
            bool need_exit = js_delay_with_flags(mjs, delay_val);
            if(need_exit) {
                mjs_return(mjs, MJS_UNDEFINED);
                return;
            }
        }
    }
    if(ln) {
        badusb->hid_api->kb_press(badusb->hid_inst, HID_KEYBOARD_RETURN);
        badusb->hid_api->kb_release(badusb->hid_inst, HID_KEYBOARD_RETURN);
    }

    mjs_return(mjs, MJS_UNDEFINED);
}

static void js_badusb_print(struct mjs* mjs) {
    badusb_print(mjs, false, false);
}

static void js_badusb_println(struct mjs* mjs) {
    badusb_print(mjs, true, false);
}

static void js_badusb_alt_print(struct mjs* mjs) {
    badusb_print(mjs, false, true);
}

static void js_badusb_alt_println(struct mjs* mjs) {
    badusb_print(mjs, true, true);
}

static void* js_badusb_create(struct mjs* mjs, mjs_val_t* object, JsModules* modules) {
    UNUSED(modules);
    JsBadusbInst* badusb = malloc(sizeof(JsBadusbInst));
    memset(badusb, 0, sizeof(JsBadusbInst));
    js_badusb_reset_layout(badusb);
    mjs_val_t badusb_obj = mjs_mk_object(mjs);
    mjs_set(mjs, badusb_obj, INST_PROP_NAME, ~0, mjs_mk_foreign(mjs, badusb));
    mjs_set(mjs, badusb_obj, "setup", ~0, MJS_MK_FN(js_badusb_setup));
    mjs_set(mjs, badusb_obj, "setupBle", ~0, MJS_MK_FN(js_badusb_setup_ble));
    mjs_set(mjs, badusb_obj, "quit", ~0, MJS_MK_FN(js_badusb_quit));
    mjs_set(mjs, badusb_obj, "isConnected", ~0, MJS_MK_FN(js_badusb_is_connected));
    mjs_set(mjs, badusb_obj, "getLockState", ~0, MJS_MK_FN(js_badusb_get_lock_state));
    mjs_set(mjs, badusb_obj, "press", ~0, MJS_MK_FN(js_badusb_press));
    mjs_set(mjs, badusb_obj, "hold", ~0, MJS_MK_FN(js_badusb_hold));
    mjs_set(mjs, badusb_obj, "release", ~0, MJS_MK_FN(js_badusb_release));
    mjs_set(mjs, badusb_obj, "print", ~0, MJS_MK_FN(js_badusb_print));
    mjs_set(mjs, badusb_obj, "println", ~0, MJS_MK_FN(js_badusb_println));
    mjs_set(mjs, badusb_obj, "altPrint", ~0, MJS_MK_FN(js_badusb_alt_print));
    mjs_set(mjs, badusb_obj, "altPrintln", ~0, MJS_MK_FN(js_badusb_alt_println));
    *object = badusb_obj;
    return badusb;
}

static void js_badusb_destroy(void* inst) {
    JsBadusbInst* badusb = inst;
    js_badusb_quit_free(badusb);
    free(badusb);
}

static const JsModuleDescriptor js_badusb_desc = {
    "badusb",
    js_badusb_create,
    js_badusb_destroy,
    NULL,
};

static const FlipperAppPluginDescriptor plugin_descriptor = {
    .appid = PLUGIN_APP_ID,
    .ep_api_version = PLUGIN_API_VERSION,
    .entry_point = &js_badusb_desc,
};

const FlipperAppPluginDescriptor* js_badusb_ep(void) {
    return &plugin_descriptor;
}
