"""
Synthetic OTP version 2 memory and Option Bytes emulation for STM32WB55.
"""

import struct
from typing import Dict, Any, Optional
from ..models import DEFAULT_PROFILE, FlipperProfile

class FlipperOTP:
    """Emulates the 2 KB OTP area located at 0x1FFF7000."""
    def __init__(self, profile: Optional[FlipperProfile] = None):
        self.profile = profile or DEFAULT_PROFILE
        self.size = 2048
        self.raw_data = bytearray(self.size)
        self._generate_synthetic_otp()

    def _generate_synthetic_otp(self):
        magic = b"FURI"
        version = self.profile.hardware_otp_version
        struct.pack_into("<4sB", self.raw_data, 0, magic, version)

        struct.pack_into(
            "<BBBBBBB",
            self.raw_data,
            5,
            self.profile.hardware_target,
            self.profile.hardware_body,
            self.profile.hardware_connect,
            self.profile.hardware_display,
            self.profile.hardware_color,
            self.profile.hardware_region,
            self.profile.hardware_ver
        )

        name_bytes = self.profile.device_name.encode("ascii")[:15]
        self.raw_data[16:16 + len(name_bytes)] = name_bytes
        self.raw_data[16 + len(name_bytes)] = 0

        uid_offset = 0x590
        uid = ((self.profile.usb_vid << 64) | (self.profile.usb_pid << 32) | 0xA5C81001)
        struct.pack_into("<QQ", self.raw_data, uid_offset, uid & 0xFFFFFFFFFFFFFFFF, (uid >> 64) & 0xFFFFFFFFFFFFFFFF)

    def read_byte(self, offset: int) -> int:
        if 0 <= offset < self.size:
            return self.raw_data[offset]
        return 0xFF

    def read_word(self, offset: int) -> int:
        if 0 <= offset <= self.size - 4:
            return struct.unpack_from("<I", self.raw_data, offset)[0]
        return 0xFFFFFFFF

    def dump(self) -> bytes:
        return bytes(self.raw_data)

class OptionBytes:
    """Read-only STM32WB55 option bytes."""
    def __init__(self):
        self.RDP = 0xAA
        self.BOR_LEV = 0x00
        self.nRST_STOP = 0x01
        self.nRST_STDBY = 0x01
        self.nRST_SHDW = 0x01
        self.SRAM2_PE = 0x01
        self.SRAM2_RST = 0x01
        self.nSWBOOT0 = 0x01
        self.nBOOT0 = 0x01

    def read_register(self, reg_name: str) -> int:
        return getattr(self, reg_name, 0xFFFFFFFF)
