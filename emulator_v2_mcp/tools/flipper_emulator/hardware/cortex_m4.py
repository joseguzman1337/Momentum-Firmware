"""
ARM Cortex-M4 CPU core state and execution model for STM32WB55.
"""

from typing import Dict, List, Optional, Tuple, Any
import struct

class CortexM4Core:
    def __init__(self, clock_hz: int = 64000000):
        self.clock_hz = clock_hz
        self.r = [0] * 13
        self.sp_main = 0
        self.sp_process = 0
        self.sp_sel = 0
        self.lr = 0xFFFFFFFF
        self.pc = 0x08000000
        
        self.n_flag = False
        self.z_flag = True
        self.c_flag = False
        self.v_flag = False
        self.q_flag = False
        self.ipsr = 0
        self.thumb_bit = True
        
        self.primask = 0
        self.faultmask = 0
        self.basepri = 0
        self.control = 0
        
        self.halted = False
        self.sleeping = False
        self.cycles = 0
        self.instructions_executed = 0

    @property
    def sp(self) -> int:
        return self.sp_process if (self.control & 0x02) else self.sp_main

    @sp.setter
    def sp(self, value: int):
        if self.control & 0x02:
            self.sp_process = value & 0xFFFFFFFC
        else:
            self.sp_main = value & 0xFFFFFFFC

    @property
    def xpsr(self) -> int:
        val = (int(self.n_flag) << 31) | (int(self.z_flag) << 30) |               (int(self.c_flag) << 29) | (int(self.v_flag) << 28) |               (int(self.q_flag) << 27) | (int(self.thumb_bit) << 24) |               (self.ipsr & 0x1FF)
        return val

    @xpsr.setter
    def xpsr(self, val: int):
        self.n_flag = bool(val & (1 << 31))
        self.z_flag = bool(val & (1 << 30))
        self.c_flag = bool(val & (1 << 29))
        self.v_flag = bool(val & (1 << 28))
        self.q_flag = bool(val & (1 << 27))
        self.thumb_bit = bool(val & (1 << 24))
        self.ipsr = val & 0x1FF

    def reset(self, initial_sp: int = 0x20030000, initial_pc: int = 0x08000101):
        self.r = [0] * 13
        self.sp_main = initial_sp & 0xFFFFFFFC
        self.sp_process = initial_sp & 0xFFFFFFFC
        self.sp_sel = 0
        self.lr = 0xFFFFFFFF
        self.pc = initial_pc & 0xFFFFFFFE
        self.n_flag = False
        self.z_flag = True
        self.c_flag = False
        self.v_flag = False
        self.q_flag = False
        self.ipsr = 0
        self.thumb_bit = True
        self.primask = 0
        self.faultmask = 0
        self.basepri = 0
        self.control = 0
        self.halted = False
        self.sleeping = False
        self.cycles = 0
        self.instructions_executed = 0

    def step(self, cycles: int = 1) -> int:
        if self.halted or self.sleeping:
            self.cycles += cycles
            return cycles

        self.cycles += cycles
        self.instructions_executed += 1
        self.pc = (self.pc + 2) & 0xFFFFFFFE
        return cycles

    def trigger_exception(self, exc_number: int, handler_addr: int):
        self.ipsr = exc_number
        self.lr = 0xFFFFFFF9
        self.pc = handler_addr & 0xFFFFFFFE
        self.sleeping = False

    def return_from_exception(self):
        self.ipsr = 0

    def dump_state(self) -> Dict[str, Any]:
        return {
            "r0": f"0x{self.r[0]:08X}",
            "r1": f"0x{self.r[1]:08X}",
            "r2": f"0x{self.r[2]:08X}",
            "r3": f"0x{self.r[3]:08X}",
            "sp": f"0x{self.sp:08X}",
            "lr": f"0x{self.lr:08X}",
            "pc": f"0x{self.pc:08X}",
            "xpsr": f"0x{self.xpsr:08X}",
            "cycles": self.cycles,
            "instructions": self.instructions_executed,
            "halted": self.halted,
            "sleeping": self.sleeping
        }
