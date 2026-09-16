#include "cli_main_commands.h"

#include <furi_hal.h>
#include <furi_hal_info.h>

static void cli_command_info_callback(
    const char* key,
    const char* value,
    bool last,
    void* context) {
    UNUSED(last);
    UNUSED(context);
    printf("%-30s: %s\r\n", key, value);
}

void cli_command_info(PipeSide* pipe, FuriString* args, void* context) {
    UNUSED(pipe);

    if(context) {
        furi_hal_info_get(cli_command_info_callback, '_', NULL);
        return;
    }

    if(!furi_string_cmp(args, "device")) {
        furi_hal_info_get(cli_command_info_callback, '.', NULL);
    } else if(!furi_string_cmp(args, "power")) {
        furi_hal_power_info_get(cli_command_info_callback, '.', NULL);
    } else if(!furi_string_cmp(args, "power_debug")) {
        furi_hal_power_debug_get(cli_command_info_callback, NULL);
    } else {
        cli_print_usage("info", "<device|power|power_debug>", furi_string_get_cstr(args));
    }
}

static void cli_command_device_info(PipeSide* pipe, FuriString* args, void* context) {
    UNUSED(context);
    cli_command_info(pipe, args, (void*)true);
}

CLI_COMMAND_INTERFACE(info, cli_command_info, CliCommandFlagParallelSafe, 768, CLI_APPID);
CLI_COMMAND_INTERFACE(
    device_info, cli_command_device_info, CliCommandFlagParallelSafe, 768, CLI_APPID);
