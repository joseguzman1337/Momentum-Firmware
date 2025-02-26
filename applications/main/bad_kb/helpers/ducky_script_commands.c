#include <furi_hal.h>
#include <lib/toolbox/strint.h>
#include "ducky_script.h"
#include "ducky_script_i.h"

typedef int32_t (*DuckyCmdCallback)(BadKbScript* bad_kb, const char* line, int32_t param);

typedef struct {
    char* name;
    DuckyCmdCallback callback;
    int32_t param;
} DuckyCmd;

static int32_t ducky_fnc_delay(BadKbScript* bad_kb, const char* line, int32_t param) {
    UNUSED(param);

    line = &line[ducky_get_command_len(line) + 1];
    uint32_t delay_val = 0;
    bool state = ducky_get_number(line, &delay_val);
    if((state) && (delay_val > 0)) {
        return (int32_t)delay_val;
    }

    return ducky_error(bad_kb, "Invalid number %s", line);
}

static int32_t ducky_fnc_defdelay(BadKbScript* bad_kb, const char* line, int32_t param) {
    UNUSED(param);

    line = &line[ducky_get_command_len(line) + 1];
    bool state = ducky_get_number(line, &bad_kb->defdelay);
    if(!state) {
        return ducky_error(bad_kb, "Invalid number %s", line);
    }
    return 0;
}

static int32_t ducky_fnc_strdelay(BadKbScript* bad_kb, const char* line, int32_t param) {
    UNUSED(param);

    line = &line[ducky_get_command_len(line) + 1];
    bool state = ducky_get_number(line, &bad_kb->stringdelay);
    if(!state) {
        return ducky_error(bad_kb, "Invalid number %s", line);
    }
    return 0;
}

static int32_t ducky_fnc_defstrdelay(BadKbScript* bad_kb, const char* line, int32_t param) {
    UNUSED(param);

    line = &line[ducky_get_command_len(line) + 1];
    bool state = ducky_get_number(line, &bad_kb->defstringdelay);
    if(!state) {
        return ducky_error(bad_kb, "Invalid number %s", line);
    }
    return 0;
}

static int32_t ducky_fnc_string(BadKbScript* bad_kb, const char* line, int32_t param) {
    line = &line[ducky_get_command_len(line) + 1];
    furi_string_set_str(bad_kb->string_print, line);
    if(param == 1) {
        furi_string_cat(bad_kb->string_print, "\n");
    }

    if(bad_kb->stringdelay == 0 &&
       bad_kb->defstringdelay == 0) { // stringdelay not set - run command immediately
        bool state = ducky_string(bad_kb, furi_string_get_cstr(bad_kb->string_print));
        if(!state) {
            return ducky_error(bad_kb, "Invalid string %s", line);
        }
    } else { // stringdelay is set - run command in thread to keep handling external events
        return SCRIPT_STATE_STRING_START;
    }

    return 0;
}

static int32_t ducky_fnc_repeat(BadKbScript* bad_kb, const char* line, int32_t param) {
    UNUSED(param);

    line = &line[ducky_get_command_len(line) + 1];
    bool state = ducky_get_number(line, &bad_kb->repeat_cnt);
    if((!state) || (bad_kb->repeat_cnt == 0)) {
        return ducky_error(bad_kb, "Invalid number %s", line);
    }
    return 0;
}

static int32_t ducky_fnc_sysrq(BadKbScript* bad_kb, const char* line, int32_t param) {
    UNUSED(param);

    line = &line[ducky_get_command_len(line) + 1];
    uint16_t key = ducky_get_keycode(bad_kb, line, true);
    bad_kb->hid->kb_press(bad_kb->hid_inst, KEY_MOD_LEFT_ALT | HID_KEYBOARD_PRINT_SCREEN);
    bad_kb->hid->kb_press(bad_kb->hid_inst, key);
    bad_kb->hid->release_all(bad_kb->hid_inst);
    return 0;
}

static int32_t ducky_fnc_altchar(BadKbScript* bad_kb, const char* line, int32_t param) {
    UNUSED(param);

    line = &line[ducky_get_command_len(line) + 1];
    ducky_numlock_on(bad_kb);
    bool state = ducky_altchar(bad_kb, line);
    if(!state) {
        return ducky_error(bad_kb, "Invalid altchar %s", line);
    }
    return 0;
}

static int32_t ducky_fnc_altstring(BadKbScript* bad_kb, const char* line, int32_t param) {
    UNUSED(param);

    line = &line[ducky_get_command_len(line) + 1];
    ducky_numlock_on(bad_kb);
    bool state = ducky_altstring(bad_kb, line);
    if(!state) {
        return ducky_error(bad_kb, "Invalid altstring %s", line);
    }
    return 0;
}

static int32_t ducky_fnc_hold(BadKbScript* bad_kb, const char* line, int32_t param) {
    UNUSED(param);
    line = &line[ducky_get_command_len(line) + 1];

    if(bad_kb->key_hold_nb > (HID_KB_MAX_KEYS - 1)) {
        return ducky_error(bad_kb, "Too many keys are held");
    }

    // Handle Mouse Keys here
    uint16_t key = ducky_get_mouse_keycode_by_name(line);
    if(key != HID_MOUSE_NONE) {
        bad_kb->key_hold_nb++;
        bad_kb->hid->mouse_press(bad_kb->hid_inst, key);
        return 0;
    }

    // Handle Keyboard keys here
    key = ducky_get_keycode(bad_kb, line, true);
    if(key != HID_KEYBOARD_NONE) {
        bad_kb->key_hold_nb++;
        bad_kb->hid->kb_press(bad_kb->hid_inst, key);
        return 0;
    }

    // keyboard and mouse were none
    return ducky_error(bad_kb, "Unknown keycode for %s", line);
}

static int32_t ducky_fnc_release(BadKbScript* bad_kb, const char* line, int32_t param) {
    UNUSED(param);
    line = &line[ducky_get_command_len(line) + 1];

    if(bad_kb->key_hold_nb == 0) {
        return ducky_error(bad_kb, "No keys are held");
    }

    // Handle Mouse Keys here
    uint16_t key = ducky_get_mouse_keycode_by_name(line);
    if(key != HID_MOUSE_NONE) {
        bad_kb->key_hold_nb--;
        bad_kb->hid->mouse_release(bad_kb->hid_inst, key);
        return 0;
    }

    //Handle Keyboard Keys here
    key = ducky_get_keycode(bad_kb, line, true);
    if(key != HID_KEYBOARD_NONE) {
        bad_kb->key_hold_nb--;
        bad_kb->hid->kb_release(bad_kb->hid_inst, key);
        return 0;
    }

    // keyboard and mouse were none
    return ducky_error(bad_kb, "No keycode defined for %s", line);
}

static int32_t ducky_fnc_media(BadKbScript* bad_kb, const char* line, int32_t param) {
    UNUSED(param);

    line = &line[ducky_get_command_len(line) + 1];
    uint16_t key = ducky_get_media_keycode_by_name(line);
    if(key == HID_CONSUMER_UNASSIGNED) {
        return ducky_error(bad_kb, "No keycode defined for %s", line);
    }
    bad_kb->hid->consumer_press(bad_kb->hid_inst, key);
    bad_kb->hid->consumer_release(bad_kb->hid_inst, key);
    return 0;
}

static int32_t ducky_fnc_globe(BadKbScript* bad_kb, const char* line, int32_t param) {
    UNUSED(param);

    line = &line[ducky_get_command_len(line) + 1];
    uint16_t key = ducky_get_keycode(bad_kb, line, true);
    if(key == HID_KEYBOARD_NONE) {
        return ducky_error(bad_kb, "No keycode defined for %s", line);
    }

    bad_kb->hid->consumer_press(bad_kb->hid_inst, HID_CONSUMER_FN_GLOBE);
    bad_kb->hid->kb_press(bad_kb->hid_inst, key);
    bad_kb->hid->kb_release(bad_kb->hid_inst, key);
    bad_kb->hid->consumer_release(bad_kb->hid_inst, HID_CONSUMER_FN_GLOBE);
    return 0;
}

static int32_t ducky_fnc_waitforbutton(BadKbScript* bad_kb, const char* line, int32_t param) {
    UNUSED(param);
    UNUSED(bad_kb);
    UNUSED(line);

    return SCRIPT_STATE_WAIT_FOR_BTN;
}

static int32_t ducky_fnc_mouse_scroll(BadKbScript* bad_kb, const char* line, int32_t param) {
    UNUSED(param);

    line = &line[strcspn(line, " ") + 1];
    int32_t mouse_scroll_dist = 0;

    if(strint_to_int32(line, NULL, &mouse_scroll_dist, 10) != StrintParseNoError) {
        return ducky_error(bad_kb, "Invalid Number %s", line);
    }

    bad_kb->hid->mouse_scroll(bad_kb->hid_inst, mouse_scroll_dist);

    return 0;
}

static int32_t ducky_fnc_mouse_move(BadKbScript* bad_kb, const char* line, int32_t param) {
    UNUSED(param);

    line = &line[strcspn(line, " ") + 1];
    int32_t mouse_move_x = 0;
    int32_t mouse_move_y = 0;

    if(strint_to_int32(line, NULL, &mouse_move_x, 10) != StrintParseNoError) {
        return ducky_error(bad_kb, "Invalid Number %s", line);
    }

    line = &line[strcspn(line, " ") + 1];

    if(strint_to_int32(line, NULL, &mouse_move_y, 10) != StrintParseNoError) {
        return ducky_error(bad_kb, "Invalid Number %s", line);
    }

    bad_kb->hid->mouse_move(bad_kb->hid_inst, mouse_move_x, mouse_move_y);

    return 0;
}

static const DuckyCmd ducky_commands[] = {
    {"REM", NULL, -1},
    {"ID", NULL, -1},
    {"BT_ID", NULL, -1},
    {"BLE_ID", NULL, -1},
    {"DELAY", ducky_fnc_delay, -1},
    {"STRING", ducky_fnc_string, 0},
    {"STRINGLN", ducky_fnc_string, 1},
    {"DEFAULT_DELAY", ducky_fnc_defdelay, -1},
    {"DEFAULTDELAY", ducky_fnc_defdelay, -1},
    {"STRINGDELAY", ducky_fnc_strdelay, -1},
    {"STRING_DELAY", ducky_fnc_strdelay, -1},
    {"DEFAULT_STRING_DELAY", ducky_fnc_defstrdelay, -1},
    {"DEFAULTSTRINGDELAY", ducky_fnc_defstrdelay, -1},
    {"REPEAT", ducky_fnc_repeat, -1},
    {"SYSRQ", ducky_fnc_sysrq, -1},
    {"ALTCHAR", ducky_fnc_altchar, -1},
    {"ALTSTRING", ducky_fnc_altstring, -1},
    {"ALTCODE", ducky_fnc_altstring, -1},
    {"HOLD", ducky_fnc_hold, -1},
    {"RELEASE", ducky_fnc_release, -1},
    {"WAIT_FOR_BUTTON_PRESS", ducky_fnc_waitforbutton, -1},
    {"MEDIA", ducky_fnc_media, -1},
    {"GLOBE", ducky_fnc_globe, -1},
    {"MOUSEMOVE", ducky_fnc_mouse_move, -1},
    {"MOUSE_MOVE", ducky_fnc_mouse_move, -1},
    {"MOUSESCROLL", ducky_fnc_mouse_scroll, -1},
    {"MOUSE_SCROLL", ducky_fnc_mouse_scroll, -1},
};

#define TAG "BadKb"

#define WORKER_TAG TAG "Worker"

int32_t ducky_execute_cmd(BadKbScript* bad_kb, const char* line) {
    size_t cmd_word_len = strcspn(line, " ");
    for(size_t i = 0; i < COUNT_OF(ducky_commands); i++) {
        size_t cmd_compare_len = strlen(ducky_commands[i].name);

        if(cmd_compare_len != cmd_word_len) {
            continue;
        }

        if(strncmp(line, ducky_commands[i].name, cmd_compare_len) == 0) {
            if(ducky_commands[i].callback == NULL) {
                return 0;
            } else {
                return (ducky_commands[i].callback)(bad_kb, line, ducky_commands[i].param);
            }
        }
    }

    return SCRIPT_STATE_CMD_UNKNOWN;
}
