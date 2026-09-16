from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EXTERNAL = ROOT / "applications" / "external"

GPIO_ESP_APPS = {
    "camera_suite": "camera_suite",
    "cognitive_agent": "cognitive_agent",
    "esp8266_deauth": "esp8266_deauther",
    "esp_flasher": "esp_flasher",
    "evil_portal": "evil_portal",
    "ghost_esp": "ghost_esp",
    "ifttt": "esp8266_ifttt_virtual_button",
    "wardriver": "wardriver",
    "wifi_deauther": "esp8266_wifi_deauther_v2",
    "wifi_marauder_companion": "esp32_wifi_marauder",
    "wifi_scanner": "wifi_scanner",
}

UART_STARTUP_SEQUENCES = {
    "camera_suite/views/camera_suite_view_camera.c": [
        ("camera_on_irq_cb", "instance->camera_worker_thread"),
    ],
    "esp8266_deauth/esp8266_deauth.c": [("uart_on_irq_cb", "app->m_worker_thread")],
    "esp_flasher/esp_flasher_uart.c": [("esp_flasher_uart_on_irq_cb", "uart->rx_thread")],
    "evil_portal/evil_portal_uart.c": [("evil_portal_uart_on_irq_cb", "uart->rx_thread")],
    "wardriver/wardriver_uart.c": [
        ("uart_cb_esp", "ctx->thread_esp"),
        ("uart_cb_gps", "ctx->thread_gps"),
    ],
    "wifi_deauther/wifi_deauther_uart.c": [
        ("wifi_deauther_uart_on_irq_cb", "uart->rx_thread"),
    ],
    "wifi_marauder_companion/wifi_marauder_uart.c": [
        ("wifi_marauder_uart_on_irq_cb", "uart->rx_thread"),
    ],
    "wifi_scanner/wifi_scanner.c": [("uart_on_irq_cb", "app->m_worker_thread")],
}


def test_gpio_esp_menu_inventory_is_complete():
    discovered = {}
    for manifest in EXTERNAL.glob("*/application.fam"):
        text = manifest.read_text()
        if 'fap_category="GPIO/ESP"' not in text:
            continue
        for appid in GPIO_ESP_APPS.values():
            if f'appid="{appid}"' in text:
                discovered[manifest.parent.name] = appid
                break

    assert discovered == GPIO_ESP_APPS


def test_uart_workers_start_before_async_receiver():
    for relative_path, sequences in UART_STARTUP_SEQUENCES.items():
        source = (EXTERNAL / relative_path).read_text()
        for callback, thread in sequences:
            callback_position = source.index(callback)
            worker = source.index(f"furi_thread_start({thread});", callback_position)
            receiver = source.index("furi_hal_serial_async_rx_start(", worker)
            assert worker < receiver, f"{relative_path}: UART RX starts before {thread}"


def test_apps_restore_preexisting_otg_power_state():
    for relative_path in (
        "esp8266_deauth/esp8266_deauth.c",
        "wifi_scanner/wifi_scanner.c",
        "wardriver/wardriver.c",
    ):
        source = (EXTERNAL / relative_path).read_text()
        assert "otg_was_enabled = furi_hal_power_is_otg_enabled()" in source
        assert "furi_hal_power_is_otg_enabled() && !otg_was_enabled" in source


def test_wardriver_never_indexes_an_empty_scan_result():
    source = (EXTERNAL / "wardriver/wardriver.c").read_text()
    assert source.count("ctx->access_points_count > 0") >= 3


def test_wifi_marauder_scan_defaults_to_compatible_ap_command():
    menu = (
        EXTERNAL
        / "wifi_marauder_companion/scenes/wifi_marauder_scene_start.c"
    ).read_text()
    uart = (EXTERNAL / "wifi_marauder_companion/wifi_marauder_uart.c").read_text()
    app = (EXTERNAL / "wifi_marauder_companion/wifi_marauder_app.c").read_text()

    scan_item = menu[menu.index('{"Scan",') : menu.index('{"SSID",')]
    assert '{"ap", "station", "all", "ping", "arp"}' in scan_item
    assert '{"scanap", "scansta", "scanall", "pingscan", "arpscan"}' in scan_item
    assert "calloc(1, sizeof(WifiMarauderUart))" in uart
    assert "calloc(1, sizeof(WifiMarauderApp))" in app
