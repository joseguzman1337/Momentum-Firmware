import csv
import json
import re
from pathlib import Path


ROOT = Path(__file__).parents[1]
TARGET = ROOT / "targets/f7/target.json"
API_SYMBOLS = ROOT / "targets/f7/api_symbols.csv"
USB_CORE = ROOT / "targets/f7/furi_hal/furi_hal_usb.c"
USB_ETH_MANIFEST = ROOT / "applications/external/usb_ethernet/application.fam"
CLI_MANIFEST = ROOT / "applications/services/cli/application.fam"
FLASH_AND_SETUP = ROOT / "scripts/flash_and_setup_ethernet.sh"
POST_FLASH_USB_ETH = ROOT / "scripts/fbt_hooks/post_flash_usb_ethernet.py"
HOTPLUG_USB_ETH = ROOT / "scripts/flipper-auto-ethernet-setup.sh"
CLI_BOOTSTRAP = ROOT / "applications/services/cli/cli_bootstrap_commands.c"
CLI_REGISTRY = ROOT / "lib/toolbox/cli/cli_registry.c"
LWIP_FREERTOS_API = {
    "vPortEnterCritical",
    "vPortExitCritical",
    "vQueueDelete",
    "vTaskDelete",
    "vTaskSuspend",
    "xQueueCreateMutex",
    "xQueueTakeMutexRecursive",
    "xQueueGenericCreate",
    "xTaskCreate",
    "xQueueGiveMutexRecursive",
    "xTaskGetTickCount",
    "xQueueReceive",
    "xQueueSemaphoreTake",
    "xQueueGenericSend",
}


def test_usb_ethernet_and_lwip_are_not_linked_into_f7_core():
    target = json.loads(TARGET.read_text())

    assert "furi_hal_usb_eth.c" in target["excluded_sources"]
    assert "furi_hal_usb_eth.h" in target["excluded_headers"]
    assert "lwip" not in target["linker_dependencies"]


def test_externalized_usb_ethernet_is_not_advertised_as_core_sdk_api():
    with API_SYMBOLS.open(newline="") as api_file:
        rows = list(csv.reader(api_file))

    exported_names = {row[2] for row in rows if len(row) > 2 and row[1] == "+"}
    assert "targets/furi_hal_include/furi_hal_usb_eth.h" not in exported_names
    assert "furi_hal_usb_eth_http_download_to_file" not in exported_names
    assert "furi_hal_usb_eth_ping" not in exported_names
    assert "usb_eth" not in exported_names


def test_private_lwip_has_only_its_required_kernel_relocations_exported():
    with API_SYMBOLS.open(newline="") as api_file:
        rows = list(csv.reader(api_file))

    exported_names = {row[2] for row in rows if len(row) > 2 and row[1] == "+"}
    assert LWIP_FREERTOS_API <= exported_names

    bridge = (ROOT / "targets/furi_hal_include/furi_hal_usb_eth_freertos.h").read_text()
    for symbol in LWIP_FREERTOS_API:
        assert symbol in bridge
    declared_functions = set(
        re.findall(r"\b((?:vPort|vQueue|vTask|xQueue|xTask)\w+)\s*\(", bridge)
    )
    assert declared_functions == LWIP_FREERTOS_API


def test_core_usb_keeps_cdc_vcp_and_has_no_ethernet_dependency():
    source = USB_CORE.read_text()

    assert "#include <furi_hal_usb_cdc.h>" in source
    assert "usb.interface = NULL;" in source
    assert "furi_hal_usb_eth.h" not in source


def test_scoped_fap_and_fal_apps_are_on_demand_types():
    usb_manifest = USB_ETH_MANIFEST.read_text()
    cli_manifest = CLI_MANIFEST.read_text()

    usb_app = usb_manifest[usb_manifest.index('appid="usb_ethernet"') : usb_manifest.index('appid="cli_ping"')]
    assert "FlipperAppType.EXTERNAL" in usb_app
    assert "FlipperAppType.STARTUP" not in usb_app
    assert "FlipperAppType.SERVICE" not in usb_app

    for appid in re.findall(r'appid="(cli_[a-z0-9_]+)"', cli_manifest):
        app = cli_manifest[cli_manifest.index(f'appid="{appid}"') :]
        app = app[: app.index("\n)")]
        if appid != "cli_vcp":
            assert "FlipperAppType.PLUGIN" in app


def test_usb_ethernet_host_automation_is_explicit_opt_in():
    flash_script = FLASH_AND_SETUP.read_text()
    post_flash = POST_FLASH_USB_ETH.read_text()
    hotplug = HOTPLUG_USB_ETH.read_text()

    assert "ENABLE_USB_ETHERNET=0" in flash_script
    assert "--enable-usb-ethernet" in flash_script
    assert "flash_devboard" in flash_script
    assert 'post_flash_usb_ethernet.py\" --enable' in flash_script
    assert 'if not args.enable:' in post_flash
    assert "USB Ethernet autostart is disabled" in post_flash
    assert 'start)\n        log "USB Ethernet autostart is disabled' in hotplug
    assert "enable)" in hotplug


def test_host_queried_device_info_stays_builtin_and_cannot_be_shadowed():
    cli_manifest = CLI_MANIFEST.read_text()
    bootstrap = CLI_BOOTSTRAP.read_text()
    registry = CLI_REGISTRY.read_text()

    core_app = cli_manifest[: cli_manifest.index("\n)\n")]
    assert '"cli_info_command.c"' in core_app
    assert 'registry, "device_info"' in bootstrap
    assert 'registry, "info"' in bootstrap
    assert "plugin_manager_load_single" not in bootstrap
    assert "if(CliCommandDict_get(registry->commands, plugin_name)) continue;" in registry


def test_usb_boot_starts_without_a_phantom_initialized_interface():
    usb_hal = (ROOT / "targets/f7/furi_hal/furi_hal_usb.c").read_text()

    assert "usb.interface = NULL;" in usb_hal
    assert "usb.interface = &usb_cdc_dual;" not in usb_hal
    assert "usb.interface = &usb_eth;" not in usb_hal
