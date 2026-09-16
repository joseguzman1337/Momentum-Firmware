"""
RCC (Reset and Clock Control) and RTC (Real-Time Clock) emulation for STM32WB55.
"""

import time
from typing import Dict, Any

class RCCController:
    def __init__(self):
        self.cr = 0x07015505
        self.cfgr = 0x0000000C
        self.ahb1enr = 0x00000000
        self.ahb2enr = 0x0000003F
        self.ahb3enr = 0x00020000
        self.apb1enr1 = 0x00000000
        self.apb1enr2 = 0x00000000
        self.apb2enr = 0x00000000
        self.cpu1_freq_hz = 64000000
        self.cpu2_freq_hz = 32000000

    def read_register(self, offset: int, length: int = 4) -> int:
        if offset == 0x00: return self.cr
        elif offset == 0x08: return self.cfgr
        elif offset == 0x48: return self.ahb1enr
        elif offset == 0x4C: return self.ahb2enr
        elif offset == 0x50: return self.ahb3enr
        elif offset == 0x58: return self.apb1enr1
        elif offset == 0x5C: return self.apb1enr2
        elif offset == 0x60: return self.apb2enr
        return 0

    def write_register(self, offset: int, val: int, length: int = 4):
        if offset == 0x00: self.cr = val | 0x07000000
        elif offset == 0x08: self.cfgr = val
        elif offset == 0x48: self.ahb1enr = val
        elif offset == 0x4C: self.ahb2enr = val
        elif offset == 0x50: self.ahb3enr = val
        elif offset == 0x58: self.apb1enr1 = val
        elif offset == 0x5C: self.apb1enr2 = val
        elif offset == 0x60: self.apb2enr = val

class RTCController:
    def __init__(self):
        self.cr = 0
        self.isr = 0x00000027
        self.prer = 0x007F00FF

    def _to_bcd(self, val: int) -> int:
        return ((val // 10) << 4) | (val % 10)

    def _from_bcd(self, bcd: int) -> int:
        return ((bcd >> 4) * 10) + (bcd & 0x0F)

    def get_time_register(self) -> int:
        now = time.localtime()
        ht = self._to_bcd(now.tm_hour)
        mnt = self._to_bcd(now.tm_min)
        st = self._to_bcd(now.tm_sec)
        return (ht << 16) | (mnt << 8) | st

    def get_date_register(self) -> int:
        now = time.localtime()
        yt = self._to_bcd(now.tm_year % 100)
        wdu = now.tm_wday + 1
        mt = self._to_bcd(now.tm_mon)
        dt = self._to_bcd(now.tm_mday)
        return (yt << 24) | (wdu << 21) | (mt << 8) | dt

    def read_register(self, offset: int, length: int = 4) -> int:
        if offset == 0x00: return self.get_time_register()
        elif offset == 0x04: return self.get_date_register()
        elif offset == 0x08: return self.cr
        elif offset == 0x0C: return self.isr
        elif offset == 0x10: return self.prer
        return 0

    def write_register(self, offset: int, val: int, length: int = 4):
        if offset == 0x08: self.cr = val
        elif offset == 0x0C: self.isr = val | 0x20
        elif offset == 0x10: self.prer = val
