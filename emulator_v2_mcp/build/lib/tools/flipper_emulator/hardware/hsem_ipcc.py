"""
Hardware Semaphore (HSEM) and Inter-Processor Communication Controller (IPCC) emulation.
"""

class HSEMController:
    def __init__(self):
        self.semaphores = [0] * 32
        self.c1_ier = 0
        self.c1_icr = 0
        self.c1_isr = 0
        self.c1_misr = 0

    def take_semaphore(self, sem_id: int, proc_id: int = 1, core_id: int = 1) -> bool:
        if not (0 <= sem_id < 32): return False
        if self.semaphores[sem_id] == 0:
            self.semaphores[sem_id] = (core_id << 8) | (proc_id & 0xFF) | 0x80000000
            return True
        return False

    def release_semaphore(self, sem_id: int, proc_id: int = 1, core_id: int = 1) -> bool:
        if not (0 <= sem_id < 32): return False
        owner = (core_id << 8) | (proc_id & 0xFF) | 0x80000000
        if self.semaphores[sem_id] == owner:
            self.semaphores[sem_id] = 0
            if self.c1_ier & (1 << sem_id):
                self.c1_misr |= (1 << sem_id)
            return True
        return False

    def read_register(self, offset: int, length: int = 4) -> int:
        if 0x00 <= offset < 0x80:
            return self.semaphores[offset // 4]
        elif 0x80 <= offset < 0x100:
            sem_id = (offset - 0x80) // 4
            self.take_semaphore(sem_id, proc_id=1, core_id=1)
            return self.semaphores[sem_id]
        elif offset == 0x100: return self.c1_ier
        elif offset == 0x104: return self.c1_icr
        elif offset == 0x108: return self.c1_isr
        elif offset == 0x10C: return self.c1_misr
        return 0

    def write_register(self, offset: int, val: int, length: int = 4):
        if 0x00 <= offset < 0x80:
            sem_id = offset // 4
            if (val & 0xFF) != 0:
                self.take_semaphore(sem_id, proc_id=val & 0xFF, core_id=(val >> 8) & 0x0F)
            else:
                self.release_semaphore(sem_id, proc_id=1, core_id=1)
        elif offset == 0x100: self.c1_ier = val
        elif offset == 0x104:
            self.c1_icr = val
            self.c1_misr &= ~val

class IPCCController:
    def __init__(self):
        self.c1_to_c2_status = 0
        self.c2_to_c1_status = 0
        self.c1_mr = 0x003F003F
        self.c1_cr = 0x00000000

    def send_c1_to_c2(self, channel: int):
        if 0 <= channel < 6: self.c1_to_c2_status |= (1 << channel)

    def acknowledge_c1_from_c2(self, channel: int):
        if 0 <= channel < 6: self.c1_to_c2_status &= ~(1 << channel)

    def notify_c2_to_c1(self, channel: int):
        if 0 <= channel < 6: self.c2_to_c1_status |= (1 << channel)

    def read_register(self, offset: int, length: int = 4) -> int:
        if offset == 0x00: return self.c1_cr
        elif offset == 0x04: return self.c1_mr
        elif offset == 0x0C: return self.c1_to_c2_status
        elif offset == 0x14: return self.c2_to_c1_status
        return 0

    def write_register(self, offset: int, val: int, length: int = 4):
        if offset == 0x00: self.c1_cr = val
        elif offset == 0x04: self.c1_mr = val
        elif offset == 0x08:
            self.c1_to_c2_status &= ~(val & 0x3F)
            self.c2_to_c1_status &= ~((val >> 16) & 0x3F)
