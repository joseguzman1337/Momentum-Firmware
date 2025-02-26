#pragma once

#ifdef __cplusplus
extern "C" {
#endif

#include <furi.h>
#include <furi_hal.h>
#include "bad_kb_hid.h"

typedef enum {
    BadKbStateInit,
    BadKbStateNotConnected,
    BadKbStateIdle,
    BadKbStateWillRun,
    BadKbStateRunning,
    BadKbStateDelay,
    BadKbStateStringDelay,
    BadKbStateWaitForBtn,
    BadKbStatePaused,
    BadKbStateDone,
    BadKbStateScriptError,
    BadKbStateFileError,
} BadKbWorkerState;

typedef struct {
    BadKbWorkerState state;
    size_t line_cur;
    size_t line_nb;
    uint32_t delay_remain;
    size_t error_line;
    char error[64];
    uint32_t elapsed;
} BadKbState;

typedef struct BadKbScript BadKbScript;

BadKbScript* bad_kb_script_open(
    FuriString* file_path,
    BadKbHidInterface* interface,
    BadKbHidConfig* hid_cfg,
    bool load_id_cfg);

void bad_kb_script_close(BadKbScript* bad_kb);

void bad_kb_script_set_keyboard_layout(BadKbScript* bad_kb, FuriString* layout_path);

void bad_kb_script_start(BadKbScript* bad_kb);

void bad_kb_script_stop(BadKbScript* bad_kb);

void bad_kb_script_start_stop(BadKbScript* bad_kb);

void bad_kb_script_pause_resume(BadKbScript* bad_kb);

BadKbState* bad_kb_script_get_state(BadKbScript* bad_kb);

#ifdef __cplusplus
}
#endif
