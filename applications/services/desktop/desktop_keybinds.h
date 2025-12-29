#pragma once

#include <furi/core/string.h>
#include <input/input.h>

#include "desktop.h"

typedef enum {
    DesktopKeybindTypePress,
    DesktopKeybindTypeHold,
    DesktopKeybindTypeMAX,
} DesktopKeybindType;

typedef enum {
    DesktopKeybindKeyUp,
    DesktopKeybindKeyDown,
    DesktopKeybindKeyRight,
    DesktopKeybindKeyLeft,
    DesktopKeybindKeyMAX,
} DesktopKeybindKey;

typedef FuriString* DesktopKeybinds[DesktopKeybindTypeMAX][DesktopKeybindKeyMAX];

#define DESKTOP_KEYBIND_DIR_PREFIX "dir:"
#define DESKTOP_KEYBIND_DIR_PREFIX_LEN (sizeof(DESKTOP_KEYBIND_DIR_PREFIX) - 1)

static inline bool desktop_keybind_is_dir(const FuriString* keybind) {
    return furi_string_start_with_str(keybind, DESKTOP_KEYBIND_DIR_PREFIX);
}

static inline const char* desktop_keybind_dir_path_cstr(const FuriString* keybind) {
    return furi_string_get_cstr(keybind) + DESKTOP_KEYBIND_DIR_PREFIX_LEN;
}

void desktop_keybinds_migrate(Desktop* desktop);
void desktop_keybinds_load(Desktop* desktop, DesktopKeybinds* keybinds);
void desktop_keybinds_save(Desktop* desktop, const DesktopKeybinds* keybinds);
void desktop_keybinds_free(DesktopKeybinds* keybinds);
void desktop_run_keybind(Desktop* desktop, InputType _type, InputKey _key);
