import csv
import json
import re
from pathlib import Path


ROOT = Path(__file__).parents[1]
TARGET = ROOT / "targets/f7/target.json"
API_SYMBOLS = ROOT / "targets/f7/api_symbols.csv"
USB_CORE = ROOT / "targets/f7/furi_hal/furi_hal_usb.c"
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
    assert "usb.interface = &usb_cdc_dual;" in source
    assert "furi_hal_usb_eth.h" not in source
