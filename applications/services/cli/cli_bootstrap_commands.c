#include "cli_main_commands.h"

#include <flipper_application/plugins/plugin_manager.h>
#include <loader/firmware_api/firmware_api.h>
#include <toolbox/cli/cli_ansi.h>

#include "usb_ethernet_broker.h"

#define CLI_DEVICE_INFO_FAL "/ext/apps_data/cli/plugins/cli_device_info.fal"

/*
 * The application-id grammar cannot represent `cli_!`, so keep only a tiny
 * forwarding alias in CPU1. Its implementation remains exclusively in the
 * device_info FAL. help, exit and reload_ext_cmds are provided by CliShell.
 */
static void cli_command_bang(PipeSide* pipe, FuriString* args, void* context) {
    UNUSED(context);

    PluginManager* manager =
        plugin_manager_alloc(CLI_APPID, CLI_PLUGIN_API_VERSION, firmware_api_interface);
    const uint32_t index = plugin_manager_get_count(manager);
    if(plugin_manager_load_single(manager, CLI_DEVICE_INFO_FAL) == PluginManagerErrorNone) {
        const CliCommandDescriptor* command = plugin_manager_get_ep(manager, index);
        furi_check(command);
        command->execute_callback(pipe, args, NULL);
    } else {
        printf(ANSI_FG_RED "failed to load external command" ANSI_RESET);
    }
    plugin_manager_free(manager);
}

void cli_main_commands_init(CliRegistry* registry) {
    cli_registry_add_command(
        registry, "!", CliCommandFlagParallelSafe, cli_command_bang, NULL);
}

void cli_on_system_start(void) {
    static UsbEthernetBroker usb_ethernet_broker;
    usb_ethernet_broker.mutex = furi_mutex_alloc(FuriMutexTypeNormal);
    furi_record_create(RECORD_USB_ETHERNET, &usb_ethernet_broker);

    CliRegistry* registry = cli_registry_alloc();
    cli_main_commands_init(registry);
    furi_record_create(RECORD_CLI, registry);
}
