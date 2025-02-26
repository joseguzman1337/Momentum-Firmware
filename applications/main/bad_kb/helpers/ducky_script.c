#include <furi.h>
#include <furi_hal.h>
#include <gui/gui.h>
#include <input/input.h>
#include <lib/toolbox/args.h>
#include <lib/toolbox/strint.h>
#include <storage/storage.h>
#include "ducky_script.h"
#include "ducky_script_i.h"
#include <dolphin/dolphin.h>

#define TAG "BadKb"

#define WORKER_TAG TAG "Worker"

#define BADKB_ASCII_TO_KEY(script, x) \
    (((uint8_t)x < 128) ? (script->layout[(uint8_t)x]) : HID_KEYBOARD_NONE)

typedef enum {
    WorkerEvtStartStop = (1 << 0),
    WorkerEvtPauseResume = (1 << 1),
    WorkerEvtEnd = (1 << 2),
    WorkerEvtConnect = (1 << 3),
    WorkerEvtDisconnect = (1 << 4),
} WorkerEvtFlags;

static const char ducky_cmd_id[] = {"ID"};
static const char ducky_cmd_bt_id[] = {"BT_ID"};
static const char ducky_cmd_ble_id[] = {"BLE_ID"};

static const uint8_t numpad_keys[10] = {
    HID_KEYPAD_0,
    HID_KEYPAD_1,
    HID_KEYPAD_2,
    HID_KEYPAD_3,
    HID_KEYPAD_4,
    HID_KEYPAD_5,
    HID_KEYPAD_6,
    HID_KEYPAD_7,
    HID_KEYPAD_8,
    HID_KEYPAD_9,
};

uint32_t ducky_get_command_len(const char* line) {
    uint32_t len = strlen(line);
    for(uint32_t i = 0; i < len; i++) {
        if(line[i] == ' ') return i;
    }
    return 0;
}

bool ducky_is_line_end(const char chr) {
    return (chr == ' ') || (chr == '\0') || (chr == '\r') || (chr == '\n');
}

uint16_t ducky_get_keycode(BadKbScript* bad_kb, const char* param, bool accept_chars) {
    uint16_t keycode = ducky_get_keycode_by_name(param);
    if(keycode != HID_KEYBOARD_NONE) {
        return keycode;
    }

    if((accept_chars) && (strlen(param) > 0)) {
        return BADKB_ASCII_TO_KEY(bad_kb, param[0]) & 0xFF;
    }
    return 0;
}

bool ducky_get_number(const char* param, uint32_t* val) {
    uint32_t value = 0;
    if(strint_to_uint32(param, NULL, &value, 10) == StrintParseNoError) {
        *val = value;
        return true;
    }
    return false;
}

void ducky_numlock_on(BadKbScript* bad_kb) {
    if((bad_kb->hid->get_led_state(bad_kb->hid_inst) & HID_KB_LED_NUM) == 0) {
        bad_kb->hid->kb_press(bad_kb->hid_inst, HID_KEYBOARD_LOCK_NUM_LOCK);
        bad_kb->hid->kb_release(bad_kb->hid_inst, HID_KEYBOARD_LOCK_NUM_LOCK);
    }
}

bool ducky_numpad_press(BadKbScript* bad_kb, const char num) {
    if((num < '0') || (num > '9')) return false;

    uint16_t key = numpad_keys[num - '0'];
    bad_kb->hid->kb_press(bad_kb->hid_inst, key);
    bad_kb->hid->kb_release(bad_kb->hid_inst, key);

    return true;
}

bool ducky_altchar(BadKbScript* bad_kb, const char* charcode) {
    uint8_t i = 0;
    bool state = false;

    bad_kb->hid->kb_press(bad_kb->hid_inst, KEY_MOD_LEFT_ALT);

    while(!ducky_is_line_end(charcode[i])) {
        state = ducky_numpad_press(bad_kb, charcode[i]);
        if(state == false) break;
        i++;
    }

    bad_kb->hid->kb_release(bad_kb->hid_inst, KEY_MOD_LEFT_ALT);
    return state;
}

bool ducky_altstring(BadKbScript* bad_kb, const char* param) {
    uint32_t i = 0;
    bool state = false;

    while(param[i] != '\0') {
        if((param[i] < ' ') || (param[i] > '~')) {
            i++;
            continue; // Skip non-printable chars
        }

        char temp_str[4];
        snprintf(temp_str, 4, "%u", param[i]);

        state = ducky_altchar(bad_kb, temp_str);
        if(state == false) break;
        i++;
    }
    return state;
}

int32_t ducky_error(BadKbScript* bad_kb, const char* text, ...) {
    va_list args;
    va_start(args, text);

    vsnprintf(bad_kb->st.error, sizeof(bad_kb->st.error), text, args);

    va_end(args);
    return SCRIPT_STATE_ERROR;
}

bool ducky_string(BadKbScript* bad_kb, const char* param) {
    uint32_t i = 0;

    while(param[i] != '\0') {
        if(param[i] != '\n') {
            uint16_t keycode = BADKB_ASCII_TO_KEY(bad_kb, param[i]);
            if(keycode != HID_KEYBOARD_NONE) {
                bad_kb->hid->kb_press(bad_kb->hid_inst, keycode);
                bad_kb->hid->kb_release(bad_kb->hid_inst, keycode);
            }
        } else {
            bad_kb->hid->kb_press(bad_kb->hid_inst, HID_KEYBOARD_RETURN);
            bad_kb->hid->kb_release(bad_kb->hid_inst, HID_KEYBOARD_RETURN);
        }
        i++;
    }
    bad_kb->stringdelay = 0;
    return true;
}

static bool ducky_string_next(BadKbScript* bad_kb) {
    if(bad_kb->string_print_pos >= furi_string_size(bad_kb->string_print)) {
        return true;
    }

    char print_char = furi_string_get_char(bad_kb->string_print, bad_kb->string_print_pos);

    if(print_char != '\n') {
        uint16_t keycode = BADKB_ASCII_TO_KEY(bad_kb, print_char);
        if(keycode != HID_KEYBOARD_NONE) {
            bad_kb->hid->kb_press(bad_kb->hid_inst, keycode);
            bad_kb->hid->kb_release(bad_kb->hid_inst, keycode);
        }
    } else {
        bad_kb->hid->kb_press(bad_kb->hid_inst, HID_KEYBOARD_RETURN);
        bad_kb->hid->kb_release(bad_kb->hid_inst, HID_KEYBOARD_RETURN);
    }

    bad_kb->string_print_pos++;

    return false;
}

static int32_t ducky_parse_line(BadKbScript* bad_kb, FuriString* line) {
    uint32_t line_len = furi_string_size(line);
    const char* line_tmp = furi_string_get_cstr(line);

    if(line_len == 0) {
        return SCRIPT_STATE_NEXT_LINE; // Skip empty lines
    }
    FURI_LOG_D(WORKER_TAG, "line:%s", line_tmp);

    // Ducky Lang Functions
    int32_t cmd_result = ducky_execute_cmd(bad_kb, line_tmp);
    if(cmd_result != SCRIPT_STATE_CMD_UNKNOWN) {
        return cmd_result;
    }

    // Mouse Keys
    uint16_t key = ducky_get_mouse_keycode_by_name(line_tmp);
    if(key != HID_MOUSE_INVALID) {
        bad_kb->hid->mouse_press(bad_kb->hid_inst, key);
        bad_kb->hid->mouse_release(bad_kb->hid_inst, key);
        return 0;
    }

    // Special keys + modifiers
    key = ducky_get_keycode(bad_kb, line_tmp, false);
    if(key == HID_KEYBOARD_NONE) {
        return ducky_error(bad_kb, "No keycode defined for %s", line_tmp);
    }
    if((key & 0xFF00) != 0) {
        // It's a modifier key
        uint32_t offset = ducky_get_command_len(line_tmp) + 1;
        // ducky_get_command_len() returns 0 without space, so check for != 1
        if(offset != 1 && line_len > offset) {
            // It's also a key combination
            line_tmp = &line_tmp[offset];
            key |= ducky_get_keycode(bad_kb, line_tmp, true);
        }
    }
    bad_kb->hid->kb_press(bad_kb->hid_inst, key);
    bad_kb->hid->kb_release(bad_kb->hid_inst, key);
    return 0;
}

static bool ducky_set_usb_id(BadKbScript* bad_kb, const char* line) {
    FuriHalUsbHidConfig* usb_hid_cfg = &bad_kb->hid_cfg->usb;

    if(sscanf(line, "%lX:%lX", &usb_hid_cfg->vid, &usb_hid_cfg->pid) == 2) {
        usb_hid_cfg->manuf[0] = '\0';
        usb_hid_cfg->product[0] = '\0';

        uint8_t id_len = ducky_get_command_len(line);
        if(!ducky_is_line_end(line[id_len + 1])) {
            sscanf(
                &line[id_len + 1],
                "%31[^\r\n:]:%31[^\r\n]",
                usb_hid_cfg->manuf,
                usb_hid_cfg->product);
        }
        FURI_LOG_D(
            WORKER_TAG,
            "set id: %04lX:%04lX mfr:%s product:%s",
            usb_hid_cfg->vid,
            usb_hid_cfg->pid,
            usb_hid_cfg->manuf,
            usb_hid_cfg->product);
        return true;
    }
    return false;
}

static bool ducky_set_ble_id(BadKbScript* bad_kb, const char* line) {
    BleProfileHidParams* ble_hid_cfg = &bad_kb->hid_cfg->ble;

    size_t line_len = strlen(line);
    size_t mac_len = sizeof(ble_hid_cfg->mac) * 3; // 2 hex chars + separator per byte
    if(line_len < mac_len + 1) return false; // MAC + at least 1 char for name

    for(size_t i = 0; i < sizeof(ble_hid_cfg->mac); i++) {
        const char* hex_byte = &line[i * 3];
        if(sscanf(hex_byte, "%02hhX", &ble_hid_cfg->mac[sizeof(ble_hid_cfg->mac) - 1 - i]) != 1) {
            return false;
        }
    }

    strlcpy(ble_hid_cfg->name, line + mac_len, sizeof(ble_hid_cfg->name));
    FURI_LOG_D(WORKER_TAG, "set ble id: %s", line);
    return true;
}

static void bad_kb_hid_state_callback(bool state, void* context) {
    furi_assert(context);
    BadKbScript* bad_kb = context;

    if(state == true) {
        furi_thread_flags_set(furi_thread_get_id(bad_kb->thread), WorkerEvtConnect);
    } else {
        furi_thread_flags_set(furi_thread_get_id(bad_kb->thread), WorkerEvtDisconnect);
    }
}

static bool ducky_script_preload(BadKbScript* bad_kb, File* script_file) {
    uint8_t ret = 0;
    uint32_t line_len = 0;

    furi_string_reset(bad_kb->line);

    do {
        ret = storage_file_read(script_file, bad_kb->file_buf, FILE_BUFFER_LEN);
        for(uint16_t i = 0; i < ret; i++) {
            if(bad_kb->file_buf[i] == '\n' && line_len > 0) {
                bad_kb->st.line_nb++;
                line_len = 0;
            } else {
                if(bad_kb->st.line_nb == 0) { // Save first line
                    furi_string_push_back(bad_kb->line, bad_kb->file_buf[i]);
                }
                line_len++;
            }
        }
        if(storage_file_eof(script_file)) {
            if(line_len > 0) {
                bad_kb->st.line_nb++;
                break;
            }
        }
    } while(ret > 0);

    if(bad_kb->load_id_cfg) {
        const char* line_tmp = furi_string_get_cstr(bad_kb->line);
        BadKbHidInterface interface = *bad_kb->interface;
        // Look for ID/BLE_ID/BT_ID command on first line
        if(strncmp(line_tmp, ducky_cmd_id, strlen(ducky_cmd_id)) == 0) {
            if(ducky_set_usb_id(bad_kb, &line_tmp[strlen(ducky_cmd_id) + 1])) {
                interface = BadKbHidInterfaceUsb;
            }
        } else if(
            strncmp(line_tmp, ducky_cmd_ble_id, strlen(ducky_cmd_ble_id)) == 0 ||
            strncmp(line_tmp, ducky_cmd_bt_id, strlen(ducky_cmd_bt_id)) == 0) {
            if(ducky_set_ble_id(bad_kb, &line_tmp[ducky_get_command_len(line_tmp) + 1])) {
                interface = BadKbHidInterfaceBle;
            }
        }

        // Auto-switch based on ID/BLE_ID/BT_ID command, user can override manually after
        if(interface != *bad_kb->interface) {
            *bad_kb->interface = interface;
            bad_kb->hid = bad_kb_hid_get_interface(*bad_kb->interface);
        }
    }

    bad_kb->hid_inst = bad_kb->hid->init(bad_kb->hid_cfg);
    bad_kb->hid->set_state_callback(bad_kb->hid_inst, bad_kb_hid_state_callback, bad_kb);

    storage_file_seek(script_file, 0, true);
    furi_string_reset(bad_kb->line);

    return true;
}

static int32_t ducky_script_execute_next(BadKbScript* bad_kb, File* script_file) {
    int32_t delay_val = 0;

    if(bad_kb->repeat_cnt > 0) {
        bad_kb->repeat_cnt--;
        delay_val = ducky_parse_line(bad_kb, bad_kb->line_prev);
        if(delay_val == SCRIPT_STATE_NEXT_LINE) { // Empty line
            return 0;
        } else if(delay_val == SCRIPT_STATE_STRING_START) { // Print string with delays
            return delay_val;
        } else if(delay_val == SCRIPT_STATE_WAIT_FOR_BTN) { // wait for button
            return delay_val;
        } else if(delay_val < 0) { // Script error
            bad_kb->st.error_line = bad_kb->st.line_cur - 1;
            FURI_LOG_E(WORKER_TAG, "Unknown command at line %zu", bad_kb->st.line_cur - 1U);
            return SCRIPT_STATE_ERROR;
        } else {
            return delay_val + bad_kb->defdelay;
        }
    }

    furi_string_set(bad_kb->line_prev, bad_kb->line);
    furi_string_reset(bad_kb->line);

    while(1) {
        if(bad_kb->buf_len == 0) {
            bad_kb->buf_len = storage_file_read(script_file, bad_kb->file_buf, FILE_BUFFER_LEN);
            if(storage_file_eof(script_file)) {
                if((bad_kb->buf_len < FILE_BUFFER_LEN) && (bad_kb->file_end == false)) {
                    bad_kb->file_buf[bad_kb->buf_len] = '\n';
                    bad_kb->buf_len++;
                    bad_kb->file_end = true;
                }
            }

            bad_kb->buf_start = 0;
            if(bad_kb->buf_len == 0) return SCRIPT_STATE_END;
        }
        for(uint8_t i = bad_kb->buf_start; i < (bad_kb->buf_start + bad_kb->buf_len); i++) {
            if(bad_kb->file_buf[i] == '\n' && furi_string_size(bad_kb->line) > 0) {
                bad_kb->st.line_cur++;
                bad_kb->buf_len = bad_kb->buf_len + bad_kb->buf_start - (i + 1);
                bad_kb->buf_start = i + 1;
                furi_string_trim(bad_kb->line);
                delay_val = ducky_parse_line(bad_kb, bad_kb->line);
                if(delay_val == SCRIPT_STATE_NEXT_LINE) { // Empty line
                    return 0;
                } else if(delay_val == SCRIPT_STATE_STRING_START) { // Print string with delays
                    return delay_val;
                } else if(delay_val == SCRIPT_STATE_WAIT_FOR_BTN) { // wait for button
                    return delay_val;
                } else if(delay_val < 0) {
                    bad_kb->st.error_line = bad_kb->st.line_cur;
                    FURI_LOG_E(WORKER_TAG, "Unknown command at line %zu", bad_kb->st.line_cur);
                    return SCRIPT_STATE_ERROR;
                } else {
                    return delay_val + bad_kb->defdelay;
                }
            } else {
                furi_string_push_back(bad_kb->line, bad_kb->file_buf[i]);
            }
        }
        bad_kb->buf_len = 0;
        if(bad_kb->file_end) return SCRIPT_STATE_END;
    }

    return 0;
}

static uint32_t bad_kb_flags_get(uint32_t flags_mask, uint32_t timeout) {
    uint32_t flags = furi_thread_flags_get();
    furi_check((flags & FuriFlagError) == 0);
    if(flags == 0) {
        flags = furi_thread_flags_wait(flags_mask, FuriFlagWaitAny, timeout);
        furi_check(((flags & FuriFlagError) == 0) || (flags == (unsigned)FuriFlagErrorTimeout));
    } else {
        uint32_t state = furi_thread_flags_clear(flags);
        furi_check((state & FuriFlagError) == 0);
    }
    return flags;
}

static int32_t bad_kb_worker(void* context) {
    BadKbScript* bad_kb = context;

    BadKbWorkerState worker_state = BadKbStateInit;
    BadKbWorkerState pause_state = BadKbStateRunning;
    int32_t delay_val = 0;

    FURI_LOG_I(WORKER_TAG, "Init");
    File* script_file = storage_file_alloc(furi_record_open(RECORD_STORAGE));
    bad_kb->line = furi_string_alloc();
    bad_kb->line_prev = furi_string_alloc();
    bad_kb->string_print = furi_string_alloc();
    bad_kb->st.elapsed = 0;

    while(1) {
        uint32_t start = furi_get_tick();
        if(worker_state == BadKbStateInit) { // State: initialization
            start = 0;
            FURI_LOG_D(WORKER_TAG, "init start");
            if(storage_file_open(
                   script_file,
                   furi_string_get_cstr(bad_kb->file_path),
                   FSAM_READ,
                   FSOM_OPEN_EXISTING)) {
                if((ducky_script_preload(bad_kb, script_file)) && (bad_kb->st.line_nb > 0)) {
                    if(bad_kb->hid->is_connected(bad_kb->hid_inst)) {
                        worker_state = BadKbStateIdle; // Ready to run
                    } else {
                        worker_state = BadKbStateNotConnected; // USB not connected
                    }
                } else {
                    worker_state = BadKbStateScriptError; // Script preload error
                }
            } else {
                FURI_LOG_E(WORKER_TAG, "File open error");
                worker_state = BadKbStateFileError; // File open error
            }
            bad_kb->st.state = worker_state;
            FURI_LOG_D(WORKER_TAG, "init done");

        } else if(worker_state == BadKbStateNotConnected) { // State: Not connected
            start = 0;
            FURI_LOG_D(WORKER_TAG, "not connected wait");
            uint32_t flags = bad_kb_flags_get(
                WorkerEvtEnd | WorkerEvtConnect | WorkerEvtDisconnect | WorkerEvtStartStop,
                FuriWaitForever);
            FURI_LOG_D(WORKER_TAG, "not connected flags: %lu", flags);

            if(flags & WorkerEvtEnd) {
                break;
            } else if(flags & WorkerEvtConnect) {
                worker_state = BadKbStateIdle; // Ready to run
            } else if(flags & WorkerEvtStartStop) {
                worker_state = BadKbStateWillRun; // Will run when connected
            }
            bad_kb->st.state = worker_state;

        } else if(worker_state == BadKbStateIdle) { // State: ready to start
            start = 0;
            FURI_LOG_D(WORKER_TAG, "idle wait");
            uint32_t flags = bad_kb_flags_get(
                WorkerEvtEnd | WorkerEvtStartStop | WorkerEvtDisconnect, FuriWaitForever);
            FURI_LOG_D(WORKER_TAG, "idle flags: %lu", flags);

            if(flags & WorkerEvtEnd) {
                break;
            } else if(flags & WorkerEvtStartStop) { // Start executing script
                dolphin_deed(DolphinDeedBadKbPlayScript);
                delay_val = 0;
                bad_kb->buf_len = 0;
                bad_kb->st.line_cur = 0;
                bad_kb->defdelay = 0;
                bad_kb->stringdelay = 0;
                bad_kb->defstringdelay = 0;
                bad_kb->repeat_cnt = 0;
                bad_kb->key_hold_nb = 0;
                bad_kb->file_end = false;
                storage_file_seek(script_file, 0, true);
                worker_state = BadKbStateRunning;
                bad_kb->st.elapsed = 0;
            } else if(flags & WorkerEvtDisconnect) {
                worker_state = BadKbStateNotConnected; // Disconnected
            }
            bad_kb->st.state = worker_state;

        } else if(worker_state == BadKbStateWillRun) { // State: start on connection
            start = 0;
            FURI_LOG_D(WORKER_TAG, "will run wait");
            uint32_t flags = bad_kb_flags_get(
                WorkerEvtEnd | WorkerEvtConnect | WorkerEvtStartStop, FuriWaitForever);
            FURI_LOG_D(WORKER_TAG, "will run flags: %lu", flags);

            if(flags & WorkerEvtEnd) {
                break;
            } else if(flags & WorkerEvtConnect) { // Start executing script
                dolphin_deed(DolphinDeedBadKbPlayScript);
                delay_val = 0;
                bad_kb->buf_len = 0;
                bad_kb->st.line_cur = 0;
                bad_kb->defdelay = 0;
                bad_kb->stringdelay = 0;
                bad_kb->defstringdelay = 0;
                bad_kb->repeat_cnt = 0;
                bad_kb->file_end = false;
                storage_file_seek(script_file, 0, true);
                // extra time for PC to recognize Flipper as keyboard
                flags = furi_thread_flags_wait(
                    WorkerEvtEnd | WorkerEvtDisconnect | WorkerEvtStartStop,
                    FuriFlagWaitAny | FuriFlagNoClear,
                    1500);
                if(flags == (unsigned)FuriFlagErrorTimeout) {
                    // If nothing happened - start script execution
                    worker_state = BadKbStateRunning;
                    bad_kb->st.elapsed = 0;
                } else if(flags & WorkerEvtStartStop) {
                    worker_state = BadKbStateIdle;
                    furi_thread_flags_clear(WorkerEvtStartStop);
                }
            } else if(flags & WorkerEvtStartStop) { // Cancel scheduled execution
                worker_state = BadKbStateNotConnected;
            }
            bad_kb->st.state = worker_state;

        } else if(worker_state == BadKbStateRunning) { // State: running
            FURI_LOG_D(WORKER_TAG, "running");
            uint16_t delay_cur = (delay_val > 100) ? (100) : (delay_val);
            uint32_t flags = furi_thread_flags_wait(
                WorkerEvtEnd | WorkerEvtStartStop | WorkerEvtPauseResume | WorkerEvtDisconnect,
                FuriFlagWaitAny,
                delay_cur);
            FURI_LOG_D(WORKER_TAG, "running flags: %lu", flags);

            delay_val -= delay_cur;
            if(!(flags & FuriFlagError)) {
                if(flags & WorkerEvtEnd) {
                    break;
                } else if(flags & WorkerEvtStartStop) {
                    worker_state = BadKbStateIdle; // Stop executing script
                    bad_kb->hid->release_all(bad_kb->hid_inst);
                } else if(flags & WorkerEvtDisconnect) {
                    worker_state = BadKbStateNotConnected; // Disconnected
                    bad_kb->hid->release_all(bad_kb->hid_inst);
                } else if(flags & WorkerEvtPauseResume) {
                    pause_state = BadKbStateRunning;
                    worker_state = BadKbStatePaused; // Pause
                }
                bad_kb->st.state = worker_state;
                bad_kb->st.elapsed += (furi_get_tick() - start);
                continue;
            } else if(
                (flags == (unsigned)FuriFlagErrorTimeout) ||
                (flags == (unsigned)FuriFlagErrorResource)) {
                if(delay_val > 0) {
                    bad_kb->st.delay_remain--;
                    bad_kb->st.elapsed += (furi_get_tick() - start);
                    continue;
                }
                bad_kb->st.state = BadKbStateRunning;
                delay_val = ducky_script_execute_next(bad_kb, script_file);
                if(delay_val == SCRIPT_STATE_ERROR) { // Script error
                    delay_val = 0;
                    worker_state = BadKbStateScriptError;
                    bad_kb->st.state = worker_state;
                    bad_kb->hid->release_all(bad_kb->hid_inst);
                } else if(delay_val == SCRIPT_STATE_END) { // End of script
                    delay_val = 0;
                    worker_state = BadKbStateIdle;
                    bad_kb->st.state = BadKbStateDone;
                    bad_kb->hid->release_all(bad_kb->hid_inst);
                    bad_kb->st.elapsed += (furi_get_tick() - start);
                    continue;
                } else if(delay_val == SCRIPT_STATE_STRING_START) { // Start printing string with delays
                    delay_val = bad_kb->defdelay;
                    bad_kb->string_print_pos = 0;
                    worker_state = BadKbStateStringDelay;
                } else if(delay_val == SCRIPT_STATE_WAIT_FOR_BTN) { // set state to wait for user input
                    worker_state = BadKbStateWaitForBtn;
                    bad_kb->st.state = BadKbStateWaitForBtn; // Show long delays
                } else if(delay_val > 100) {
                    bad_kb->st.state = BadKbStateDelay; // Show long delays
                    bad_kb->st.delay_remain = delay_val / 100;
                }
            } else {
                furi_check((flags & FuriFlagError) == 0);
            }
        } else if(worker_state == BadKbStateWaitForBtn) { // State: Wait for button Press
            start = 0;
            FURI_LOG_D(WORKER_TAG, "button wait");
            uint32_t flags = bad_kb_flags_get(
                WorkerEvtEnd | WorkerEvtStartStop | WorkerEvtPauseResume | WorkerEvtDisconnect,
                FuriWaitForever);
            FURI_LOG_D(WORKER_TAG, "button flags: %lu", flags);
            if(!(flags & FuriFlagError)) {
                if(flags & WorkerEvtEnd) {
                    break;
                } else if(flags & WorkerEvtStartStop) {
                    delay_val = 0;
                    worker_state = BadKbStateRunning;
                } else if(flags & WorkerEvtDisconnect) {
                    worker_state = BadKbStateNotConnected; // Disconnected
                    bad_kb->hid->release_all(bad_kb->hid_inst);
                }
                bad_kb->st.state = worker_state;
                continue;
            }
        } else if(worker_state == BadKbStatePaused) { // State: Paused
            start = 0;
            FURI_LOG_D(WORKER_TAG, "paused wait");
            uint32_t flags = bad_kb_flags_get(
                WorkerEvtEnd | WorkerEvtStartStop | WorkerEvtPauseResume | WorkerEvtDisconnect,
                FuriWaitForever);
            FURI_LOG_D(WORKER_TAG, "paused flags: %lu", flags);
            if(!(flags & FuriFlagError)) {
                if(flags & WorkerEvtEnd) {
                    break;
                } else if(flags & WorkerEvtStartStop) {
                    worker_state = BadKbStateIdle; // Stop executing script
                    bad_kb->st.state = worker_state;
                    bad_kb->hid->release_all(bad_kb->hid_inst);
                } else if(flags & WorkerEvtDisconnect) {
                    worker_state = BadKbStateNotConnected; // Disconnected
                    bad_kb->st.state = worker_state;
                    bad_kb->hid->release_all(bad_kb->hid_inst);
                } else if(flags & WorkerEvtPauseResume) {
                    if(pause_state == BadKbStateRunning) {
                        if(delay_val > 0) {
                            bad_kb->st.state = BadKbStateDelay;
                            bad_kb->st.delay_remain = delay_val / 100;
                        } else {
                            bad_kb->st.state = BadKbStateRunning;
                            delay_val = 0;
                        }
                        worker_state = BadKbStateRunning; // Resume
                    } else if(pause_state == BadKbStateStringDelay) {
                        bad_kb->st.state = BadKbStateRunning;
                        worker_state = BadKbStateStringDelay; // Resume
                    }
                }
                continue;
            }
        } else if(worker_state == BadKbStateStringDelay) { // State: print string with delays
            FURI_LOG_D(WORKER_TAG, "delay wait");
            uint32_t delay = (bad_kb->stringdelay == 0) ? bad_kb->defstringdelay :
                                                          bad_kb->stringdelay;
            uint32_t flags = bad_kb_flags_get(
                WorkerEvtEnd | WorkerEvtStartStop | WorkerEvtPauseResume | WorkerEvtDisconnect,
                delay);
            FURI_LOG_D(WORKER_TAG, "delay flags: %lu", flags);

            if(!(flags & FuriFlagError)) {
                if(flags & WorkerEvtEnd) {
                    break;
                } else if(flags & WorkerEvtStartStop) {
                    worker_state = BadKbStateIdle; // Stop executing script
                    bad_kb->hid->release_all(bad_kb->hid_inst);
                } else if(flags & WorkerEvtDisconnect) {
                    worker_state = BadKbStateNotConnected; // Disconnected
                    bad_kb->hid->release_all(bad_kb->hid_inst);
                } else if(flags & WorkerEvtPauseResume) {
                    pause_state = BadKbStateStringDelay;
                    worker_state = BadKbStatePaused; // Pause
                }
                bad_kb->st.state = worker_state;
                bad_kb->st.elapsed += (furi_get_tick() - start);
                continue;
            } else if(
                (flags == (unsigned)FuriFlagErrorTimeout) ||
                (flags == (unsigned)FuriFlagErrorResource)) {
                bool string_end = ducky_string_next(bad_kb);
                if(string_end) {
                    bad_kb->stringdelay = 0;
                    worker_state = BadKbStateRunning;
                }
            } else {
                furi_check((flags & FuriFlagError) == 0);
            }
        } else if(
            (worker_state == BadKbStateFileError) ||
            (worker_state == BadKbStateScriptError)) { // State: error
            start = 0;
            FURI_LOG_D(WORKER_TAG, "error wait");
            uint32_t flags =
                bad_kb_flags_get(WorkerEvtEnd, FuriWaitForever); // Waiting for exit command
            FURI_LOG_D(WORKER_TAG, "error flags: %lu", flags);

            if(flags & WorkerEvtEnd) {
                break;
            }
        }
        if(start) {
            bad_kb->st.elapsed += (furi_get_tick() - start);
        }
    }

    bad_kb->hid->set_state_callback(bad_kb->hid_inst, NULL, NULL);
    bad_kb->hid->deinit(bad_kb->hid_inst);

    storage_file_close(script_file);
    storage_file_free(script_file);
    furi_string_free(bad_kb->line);
    furi_string_free(bad_kb->line_prev);
    furi_string_free(bad_kb->string_print);

    FURI_LOG_I(WORKER_TAG, "End");

    return 0;
}

static void bad_kb_script_set_default_keyboard_layout(BadKbScript* bad_kb) {
    furi_assert(bad_kb);
    memset(bad_kb->layout, HID_KEYBOARD_NONE, sizeof(bad_kb->layout));
    memcpy(bad_kb->layout, hid_asciimap, MIN(sizeof(hid_asciimap), sizeof(bad_kb->layout)));
}

BadKbScript* bad_kb_script_open(
    FuriString* file_path,
    BadKbHidInterface* interface,
    BadKbHidConfig* hid_cfg,
    bool load_id_cfg) {
    furi_assert(file_path);

    BadKbScript* bad_kb = malloc(sizeof(BadKbScript));
    bad_kb->file_path = furi_string_alloc();
    furi_string_set(bad_kb->file_path, file_path);
    bad_kb_script_set_default_keyboard_layout(bad_kb);

    bad_kb->st.state = BadKbStateInit;
    bad_kb->st.error[0] = '\0';
    bad_kb->interface = interface;
    bad_kb->hid_cfg = hid_cfg;
    bad_kb->load_id_cfg = load_id_cfg;
    bad_kb->hid = bad_kb_hid_get_interface(*bad_kb->interface);

    bad_kb->thread = furi_thread_alloc_ex("BadKbWorker", 2048, bad_kb_worker, bad_kb);
    furi_thread_start(bad_kb->thread);
    return bad_kb;
} //-V773

void bad_kb_script_close(BadKbScript* bad_kb) {
    furi_assert(bad_kb);
    furi_thread_flags_set(furi_thread_get_id(bad_kb->thread), WorkerEvtEnd);
    furi_thread_join(bad_kb->thread);
    furi_thread_free(bad_kb->thread);
    furi_string_free(bad_kb->file_path);
    free(bad_kb);
}

void bad_kb_script_set_keyboard_layout(BadKbScript* bad_kb, FuriString* layout_path) {
    furi_assert(bad_kb);

    if((bad_kb->st.state == BadKbStateRunning) || (bad_kb->st.state == BadKbStateDelay)) {
        // do not update keyboard layout while a script is running
        return;
    }

    File* layout_file = storage_file_alloc(furi_record_open(RECORD_STORAGE));
    if(!furi_string_empty(layout_path)) { //-V1051
        if(storage_file_open(
               layout_file, furi_string_get_cstr(layout_path), FSAM_READ, FSOM_OPEN_EXISTING)) {
            uint16_t layout[128];
            if(storage_file_read(layout_file, layout, sizeof(layout)) == sizeof(layout)) {
                memcpy(bad_kb->layout, layout, sizeof(layout));
            }
        }
        storage_file_close(layout_file);
    } else {
        bad_kb_script_set_default_keyboard_layout(bad_kb);
    }
    storage_file_free(layout_file);
}

void bad_kb_script_start_stop(BadKbScript* bad_kb) {
    furi_assert(bad_kb);
    furi_thread_flags_set(furi_thread_get_id(bad_kb->thread), WorkerEvtStartStop);
}

void bad_kb_script_pause_resume(BadKbScript* bad_kb) {
    furi_assert(bad_kb);
    furi_thread_flags_set(furi_thread_get_id(bad_kb->thread), WorkerEvtPauseResume);
}

BadKbState* bad_kb_script_get_state(BadKbScript* bad_kb) {
    furi_assert(bad_kb);
    return &(bad_kb->st);
}
