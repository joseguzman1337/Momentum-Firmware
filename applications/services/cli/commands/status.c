#include "../cli_main_commands.h"
#include <furi_hal.h>

static void execute(PipeSide* pipe, FuriString* args, void* context) {
    UNUSED(pipe);
    UNUSED(args);
    UNUSED(context);
    
    uint32_t uptime = furi_get_tick() / furi_kernel_get_tick_frequency();
    printf("Flipper Status\r\n");
    printf("==============\r\n");
    printf("Device: %s\r\n", furi_hal_version_get_name_ptr());
    printf("Uptime: %luh %lum %lus\r\n", (unsigned long)(uptime / 3600), (unsigned long)((uptime / 60) % 60), (unsigned long)(uptime % 60));
    printf("Heap Free: %zu\r\n", memmgr_get_free_heap());
}

CLI_COMMAND_INTERFACE(status, execute, CliCommandFlagParallelSafe, 1024, CLI_APPID);
