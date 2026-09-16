"""
Data models, register specifications, and hardware profile definitions
for Flipper Zero Emulator v2 (Target F7B9C6 - emulator-v2).
"""

from dataclasses import dataclass, field
from enum import Enum, IntEnum
from typing import Dict, List, Optional, Any
import time

class ButtonKey(str, Enum):
    UP = "UP"
    DOWN = "DOWN"
    LEFT = "LEFT"
    RIGHT = "RIGHT"
    OK = "OK"
    BACK = "BACK"

class InputType(str, Enum):
    PRESS = "PRESS"
    RELEASE = "RELEASE"
    SHORT = "SHORT"
    LONG = "LONG"
    REPEAT = "REPEAT"

@dataclass
class InputEvent:
    key: ButtonKey
    type: InputType
    timestamp: float = field(default_factory=time.time)

class HardwareColor(IntEnum):
    BLACK = 1
    WHITE = 2

class HardwareTarget(IntEnum):
    F7 = 7

class HardwareRegion(IntEnum):
    UNKNOWN = 0
    EU = 1
    US = 2
    CA = 3
    CO = 4
    JP = 5

class SubGhzPreset(str, Enum):
    FuriHalSubGhzPreset2FSKDev238Async = "2FSK_23.8k"
    FuriHalSubGhzPreset2FSKDev476Async = "2FSK_47.6k"
    FuriHalSubGhzPresetOok270Async = "OOK_2.7k"
    FuriHalSubGhzPresetOok650Async = "OOK_6.5k"

@dataclass
class FlipperProfile:
    """Hardware profile extracted and sanitised from unit emulator-v2 (F7B9C6)."""
    device_name: str = "emulator-v2"
    hardware_model: str = "Flipper Zero"
    production_variant: str = "F7B9C6"
    hardware_ver: int = 12
    hardware_target: int = 7
    hardware_body: int = 9
    hardware_connect: int = 6
    hardware_display: int = 1
    hardware_color: int = 2  # White
    hardware_otp_version: int = 2
    hardware_region: int = 4  # Colombia (CO)
    hardware_region_name: str = "CO"
    
    # USB Identity
    usb_vid: int = 0x0483
    usb_pid: int = 0x5740
    usb_serial: str = "emulator-v2"
    usb_manufacturer: str = "Flipper Devices Inc."
    usb_product: str = "Flipper emulator-v2"
    
    # MCU & Memory
    mcu_model: str = "STM32WB55RG"
    cpu1_arch: str = "ARM Cortex-M4"
    cpu1_clock_mhz: int = 64
    cpu2_arch: str = "ARM Cortex-M0+"
    cpu2_clock_mhz: int = 32
    flash_size_bytes: int = 1024 * 1024      # 1 MB
    sram1_size_bytes: int = 192 * 1024       # 192 KB
    sram2a_size_bytes: int = 32 * 1024       # 32 KB
    sram2b_size_bytes: int = 32 * 1024       # 32 KB
    otp_size_bytes: int = 2048               # 2 KB
    
    # Radio & Stack
    wireless_stack_type: str = "BLE 5.4 / 802.15.4"
    wireless_stack_version: str = "1.20.0"
    wireless_fus_version: str = "1.2.0"
    subghz_chip: str = "TI CC1101"
    nfc_chip: str = "STMicroelectronics ST25R3916"
    rfid_type: str = "LF 125 kHz Frontend"
    infrared_rx_nm: int = 950
    infrared_tx_nm: int = 940
    
    # Battery & Power
    battery_capacity_mah: int = 2100
    charger_chip: str = "TI BQ25896"
    gauge_chip: str = "TI BQ27220 / MAX17048"
    
    # Firmware identification
    firmware_branch: str = "dev"
    firmware_commit: str = "7f0b6e1c"
    firmware_version: str = "0.88.2"
    firmware_api_major: int = 88
    firmware_api_minor: int = 2
    firmware_origin: str = "Official"
    protobuf_version_major: int = 2
    protobuf_version_minor: int = 25
    device_info_major: int = 2
    device_info_minor: int = 4

# Memory base constants
FLASH_BASE = 0x08000000
FLASH_END  = 0x08100000
SRAM1_BASE = 0x20000000
SRAM1_END  = 0x20030000
SRAM2A_BASE= 0x20030000
SRAM2A_END = 0x20038000
SRAM2B_BASE= 0x20038000
SRAM2B_END = 0x20040000
PERIPH_BASE= 0x40000000
OTP_BASE   = 0x1FFF7000
OTP_END    = 0x1FFF7800

# Inter-processor communication & Semaphores
HSEM_BASE  = 0x58001400
IPCC_BASE  = 0x58000C00
RCC_BASE   = 0x58000000
RTC_BASE   = 0x40002800

# Display resolution
SCREEN_WIDTH = 128
SCREEN_HEIGHT = 64
SCREEN_BUFFER_SIZE = (SCREEN_WIDTH * SCREEN_HEIGHT) // 8  # 1024 bytes

DEFAULT_PROFILE = FlipperProfile()
