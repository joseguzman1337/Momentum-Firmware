#include "cli_main_commands.h"

#include "usb_ethernet_broker.h"

void cli_main_commands_init(CliRegistry* registry) {
    cli_registry_add_command(
        registry, "info", CliCommandFlagParallelSafe, cli_command_info, NULL);
    cli_registry_add_command(
        registry, "device_info", CliCommandFlagParallelSafe, cli_command_info, (void*)true);
    cli_registry_add_command(
        registry, "!", CliCommandFlagParallelSafe, cli_command_info, (void*)true);
}

void cli_on_system_start(void) {
    static UsbEthernetBroker usb_ethernet_broker;
    usb_ethernet_broker.mutex = furi_mutex_alloc(FuriMutexTypeNormal);
    furi_record_create(RECORD_USB_ETHERNET, &usb_ethernet_broker);

    CliRegistry* registry = cli_registry_alloc();
    cli_main_commands_init(registry);
    furi_record_create(RECORD_CLI, registry);
}
