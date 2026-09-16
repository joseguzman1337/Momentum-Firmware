"""
Nested Vectored Interrupt Controller (NVIC) model for Cortex-M4.
"""

from typing import Dict, List, Optional
from .cortex_m4 import CortexM4Core

class NVICController:
    def __init__(self, core: CortexM4Core):
        self.core = core
        self.vtor = 0x08000000
        self.enabled = [False] * 64
        self.pending = [False] * 64
        self.active = [False] * 64
        self.priority = [0] * 64

    def set_vtor(self, addr: int):
        self.vtor = addr & 0xFFFFFF80

    def enable_irq(self, irq_num: int):
        if 0 <= irq_num < 64: self.enabled[irq_num] = True

    def disable_irq(self, irq_num: int):
        if 0 <= irq_num < 64: self.enabled[irq_num] = False

    def set_pending_irq(self, irq_num: int):
        if 0 <= irq_num < 64:
            self.pending[irq_num] = True
            self._evaluate_interrupts()

    def clear_pending_irq(self, irq_num: int):
        if 0 <= irq_num < 64: self.pending[irq_num] = False

    def is_active(self, irq_num: int) -> bool:
        return self.active[irq_num] if 0 <= irq_num < 64 else False

    def set_priority(self, irq_num: int, prio: int):
        if 0 <= irq_num < 64: self.priority[irq_num] = prio & 0xFF

    def _evaluate_interrupts(self):
        if self.core.primask != 0:
            return
        highest_prio = 256
        selected_irq = -1
        for irq in range(64):
            if self.enabled[irq] and self.pending[irq]:
                prio = self.priority[irq]
                if prio < highest_prio:
                    highest_prio = prio
                    selected_irq = irq

        if selected_irq >= 0:
            exc_num = 16 + selected_irq
            self.pending[selected_irq] = False
            self.active[selected_irq] = True
            handler = self.vtor + (exc_num * 4)
            self.core.trigger_exception(exc_num, handler)

    def read_register(self, offset: int, length: int = 4) -> int:
        if 0x000 <= offset < 0x008:
            idx = offset // 4
            val = 0
            for i in range(32):
                if self.enabled[idx * 32 + i]: val |= (1 << i)
            return val
        elif 0x080 <= offset < 0x088:
            idx = (offset - 0x080) // 4
            val = 0
            for i in range(32):
                if self.enabled[idx * 32 + i]: val |= (1 << i)
            return val
        elif 0x100 <= offset < 0x108:
            idx = (offset - 0x100) // 4
            val = 0
            for i in range(32):
                if self.pending[idx * 32 + i]: val |= (1 << i)
            return val
        elif 0x180 <= offset < 0x188:
            idx = (offset - 0x180) // 4
            val = 0
            for i in range(32):
                if self.pending[idx * 32 + i]: val |= (1 << i)
            return val
        elif 0x200 <= offset < 0x208:
            idx = (offset - 0x200) // 4
            val = 0
            for i in range(32):
                if self.active[idx * 32 + i]: val |= (1 << i)
            return val
        return 0

    def write_register(self, offset: int, val: int, length: int = 4):
        if 0x000 <= offset < 0x008:
            idx = offset // 4
            for i in range(32):
                if val & (1 << i): self.enable_irq(idx * 32 + i)
        elif 0x080 <= offset < 0x088:
            idx = (offset - 0x080) // 4
            for i in range(32):
                if val & (1 << i): self.disable_irq(idx * 32 + i)
        elif 0x100 <= offset < 0x108:
            idx = (offset - 0x100) // 4
            for i in range(32):
                if val & (1 << i): self.set_pending_irq(idx * 32 + i)
        elif 0x180 <= offset < 0x188:
            idx = (offset - 0x180) // 4
            for i in range(32):
                if val & (1 << i): self.clear_pending_irq(idx * 32 + i)
