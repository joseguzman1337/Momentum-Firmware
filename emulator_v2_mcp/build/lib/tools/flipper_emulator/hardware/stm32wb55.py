"""
STM32WB55 System Bus Arbiter and Memory Map Router.
"""

import struct
from typing import Dict, Optional, Callable, Tuple
from ..models import (
    FLASH_BASE, FLASH_END,
    SRAM1_BASE, SRAM1_END,
    SRAM2A_BASE, SRAM2A_END,
    SRAM2B_BASE, SRAM2B_END,
    OTP_BASE, OTP_END
)
from ..internal_flash.flash_manager import InternalFlashManager
from ..internal_flash.otp import FlipperOTP, OptionBytes

class STM32WB55Bus:
    def __init__(self, flash_mgr: Optional[InternalFlashManager] = None):
        self.flash_mgr = flash_mgr or InternalFlashManager()
        self.otp = FlipperOTP()
        self.option_bytes = OptionBytes()
        
        self.sram1 = bytearray(SRAM1_END - SRAM1_BASE)
        self.sram2a = bytearray(SRAM2A_END - SRAM2A_BASE)
        self.sram2b = bytearray(SRAM2B_END - SRAM2B_BASE)
        
        self.peripheral_handlers: Dict[int, Tuple[Callable[[int, int], int], Callable[[int, int, int], None]]] = {}

    def register_peripheral(self, base_addr: int, read_fn: Callable[[int, int], int], write_fn: Callable[[int, int, int], None]):
        self.peripheral_handlers[base_addr] = (read_fn, write_fn)

    def read_u32(self, addr: int) -> int:
        data = self.read_bytes(addr, 4)
        return struct.unpack("<I", data)[0]

    def read_u16(self, addr: int) -> int:
        data = self.read_bytes(addr, 2)
        return struct.unpack("<H", data)[0]

    def read_u8(self, addr: int) -> int:
        data = self.read_bytes(addr, 1)
        return data[0]

    def write_u32(self, addr: int, val: int):
        self.write_bytes(addr, struct.pack("<I", val & 0xFFFFFFFF))

    def write_u16(self, addr: int, val: int):
        self.write_bytes(addr, struct.pack("<H", val & 0xFFFF))

    def write_u8(self, addr: int, val: int):
        self.write_bytes(addr, bytes([val & 0xFF]))

    def read_bytes(self, addr: int, length: int) -> bytes:
        if FLASH_BASE <= addr < FLASH_END:
            return self.flash_mgr.read_flash_address(addr, length)

        if SRAM1_BASE <= addr < SRAM1_END:
            offset = addr - SRAM1_BASE
            if offset + length <= len(self.sram1):
                return bytes(self.sram1[offset:offset + length])
            return b"\x00" * length

        if SRAM2A_BASE <= addr < SRAM2A_END:
            offset = addr - SRAM2A_BASE
            if offset + length <= len(self.sram2a):
                return bytes(self.sram2a[offset:offset + length])
            return b"\x00" * length

        if SRAM2B_BASE <= addr < SRAM2B_END:
            offset = addr - SRAM2B_BASE
            if offset + length <= len(self.sram2b):
                return bytes(self.sram2b[offset:offset + length])
            return b"\x00" * length

        if OTP_BASE <= addr < OTP_END:
            offset = addr - OTP_BASE
            buf = bytearray(length)
            for i in range(length):
                buf[i] = self.otp.read_byte(offset + i)
            return bytes(buf)

        for base, (read_fn, _) in self.peripheral_handlers.items():
            if base <= addr < base + 0x400:
                offset = addr - base
                val = read_fn(offset, length)
                if length == 4:
                    return struct.pack("<I", val & 0xFFFFFFFF)
                elif length == 2:
                    return struct.pack("<H", val & 0xFFFF)
                else:
                    return bytes([val & 0xFF])

        return b"\x00" * length

    def write_bytes(self, addr: int, data: bytes):
        length = len(data)
        if FLASH_BASE <= addr < FLASH_END:
            self.flash_mgr.write_flash_address(addr, data)
            return

        if SRAM1_BASE <= addr < SRAM1_END:
            offset = addr - SRAM1_BASE
            if offset + length <= len(self.sram1):
                self.sram1[offset:offset + length] = data
            return

        if SRAM2A_BASE <= addr < SRAM2A_END:
            offset = addr - SRAM2A_BASE
            if offset + length <= len(self.sram2a):
                self.sram2a[offset:offset + length] = data
            return

        if SRAM2B_BASE <= addr < SRAM2B_END:
            offset = addr - SRAM2B_BASE
            if offset + length <= len(self.sram2b):
                self.sram2b[offset:offset + length] = data
            return

        for base, (_, write_fn) in self.peripheral_handlers.items():
            if base <= addr < base + 0x400:
                offset = addr - base
                if length == 4:
                    val = struct.unpack("<I", data)[0]
                elif length == 2:
                    val = struct.unpack("<H", data)[0]
                else:
                    val = data[0]
                write_fn(offset, val, length)
                return
