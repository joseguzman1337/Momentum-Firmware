"""
Oracle read-only dataset extracted from physical Flipper Zero unit 'emulator-v2'.
Used for deterministic replay, reference assertions, and synthetic OTP generation.
"""

from typing import Dict, Any

ORACLE_V2_DATA: Dict[str, Any] = {
    "device": {
        "name": "emulator-v2",
        "model": "Flipper Zero",
        "variant": "F7B9C6",
        "hardware_ver": 12,
        "hardware_target": 7,
        "hardware_body": 9,
        "hardware_connect": 6,
        "hardware_display": 1,
        "hardware_color": 2,
        "hardware_color_name": "White",
        "hardware_otp_version": 2,
        "hardware_region": 4,
        "hardware_region_name": "CO",
        "hardware_timestamp": 1699900000,
        "vendor": "Flipper Devices Inc.",
        "vendor_id": 1155,
        "product_id": 22336,
        "serial": "emulator-v2",
    },
    "firmware": {
        "branch": "dev",
        "commit": "7f0b6e1c",
        "version": "0.88.2",
        "api_version_major": 88,
        "api_version_minor": 2,
        "origin": "Official",
        "target": "f7",
        "build_date": "2026-09-10",
        "protobuf_version_major": 2,
        "protobuf_version_minor": 25,
    },
    "hardware_specs": {
        "mcu": "STM32WB55RGV6",
        "cpu1": {"arch": "Cortex-M4", "freq_hz": 64000000, "fpu": True},
        "cpu2": {"arch": "Cortex-M0+", "freq_hz": 32000000, "stack": "1.20.0", "fus": "1.2.0"},
        "flash": {"base": 0x08000000, "size_bytes": 1048576},
        "sram1": {"base": 0x20000000, "size_bytes": 196608},
        "sram2a": {"base": 0x20030000, "size_bytes": 32768},
        "sram2b": {"base": 0x20038000, "size_bytes": 32768},
        "otp": {"base": 0x1FFF7000, "size_bytes": 2048, "version": 2},
        "display": {"driver": "ST7567", "width": 128, "height": 64, "interface": "SPI"},
        "subghz": {"chip": "CC1101", "bands": [300000000, 348000000, 387000000, 464000000, 779000000, 928000000]},
        "nfc": {"chip": "ST25R3916", "frequency_hz": 13560000},
        "rfid": {"frequency_hz": 125000, "protocols": ["EM4100", "HIDProx", "Indala"]},
        "ir": {"tx_nm": 940, "rx_nm": 950},
        "ibutton": {"protocols": ["Dallas_DS1990A", "Cyfral", "Metakom"]},
        "gpio": {"num_pins": 13, "headers": ["1-18"]},
        "battery": {"capacity_mah": 2100, "gauge": "BQ27220", "charger": "BQ25896"}
    },
    "sd_fixture_summary": {
        "total_files": 973,
        "total_size_mb": 27.4,
        "directories": [
            "apps", "subghz", "nfc", "lfrfid", "ibutton",
            "infrared", "badusb", "update_resources", "wav_player",
            "u2f", "picopass", "music_player"
        ]
    }
}

def get_oracle_data() -> Dict[str, Any]:
    return ORACLE_V2_DATA
