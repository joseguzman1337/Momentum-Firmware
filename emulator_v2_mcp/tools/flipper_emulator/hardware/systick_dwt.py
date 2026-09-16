"""
SysTick Timer and DWT Cycle Counter emulation for Cortex-M4.
"""

from typing import Optional
from .cortex_m4 import CortexM4Core

class SysTickTimer:
    def __init__(self, core: CortexM4Core):
        self.core = core
        self.ctrl = 0
        self.load = 64000 - 1
        self.val = 0
        self.calib = 64000

    def step(self, cycles: int = 1) -> bool:
        if not (self.ctrl & 0x01):
            return False

        fired = False
        if self.val < cycles:
            self.val = self.load - (cycles - self.val)
            self.ctrl |= (1 << 16)
            if self.ctrl & 0x02:
                self.core.trigger_exception(15, 0x0800003C)
                fired = True
        else:
            self.val -= cycles
        return fired

    def read_register(self, offset: int, length: int = 4) -> int:
        if offset == 0x00:
            val = self.ctrl
            self.ctrl &= ~(1 << 16)
            return val
        elif offset == 0x04: return self.load
        elif offset == 0x08: return self.val
        elif offset == 0x0C: return self.calib
        return 0

    def write_register(self, offset: int, val: int, length: int = 4):
        if offset == 0x00: self.ctrl = val & 0x00010007
        elif offset == 0x04: self.load = val & 0x00FFFFFF
        elif offset == 0x08:
            self.val = 0
            self.ctrl &= ~(1 << 16)


class DWTCounter:
    def __init__(self, core: CortexM4Core):
        self.core = core
        self.ctrl = 0x40000000
        self.cyccnt_enabled = True

    def get_cycles(self) -> int:
        return self.core.cycles & 0xFFFFFFFF

    def read_register(self, offset: int, length: int = 4) -> int:
        if offset == 0x00:
            return self.ctrl | (1 if self.cyccnt_enabled else 0)
        elif offset == 0x04:
            return self.get_cycles()
        return 0

    def write_register(self, offset: int, val: int, length: int = 4):
        if offset == 0x00:
            self.cyccnt_enabled = bool(val & 0x01)
        elif offset == 0x04:
            self.core.cycles = val & 0xFFFFFFFF
