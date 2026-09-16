"""
TI CC1101 Sub-GHz Transceiver Emulation for Flipper Zero.
"""

from typing import Dict, List, Optional, Any
from ..models import SubGhzPreset

class CC1101Transceiver:
    def __init__(self, region_code: int = 4):
        self.region_code = region_code
        self.frequency_hz = 433920000
        self.preset = SubGhzPreset.FuriHalSubGhzPreset2FSKDev476Async
        self.rssi_dbm = -65.0
        self.mode = "IDLE"
        self.registers: Dict[int, int] = {
            0x00: 0x29, 0x01: 0x2E, 0x02: 0x06, 0x03: 0x07, 0x04: 0xD3, 0x05: 0x91,
            0x06: 0xFF, 0x07: 0x04, 0x08: 0x05, 0x09: 0x00, 0x0A: 0x00, 0x0B: 0x06,
            0x0C: 0x00, 0x0D: 0x10, 0x0E: 0xB1, 0x0F: 0x3B, 0x10: 0xF8, 0x11: 0x83,
            0x12: 0x13, 0x13: 0x22, 0x14: 0xF8, 0x15: 0x15, 0x16: 0x07, 0x17: 0x30,
            0x18: 0x18,
        }
        self.tx_history: List[Dict[str, Any]] = []
        self.rx_buffer: List[Dict[str, Any]] = []

    def is_frequency_allowed(self, freq_hz: int) -> bool:
        if 433050000 <= freq_hz <= 434790000: return True
        if 902000000 <= freq_hz <= 928000000: return True
        if 310000000 <= freq_hz <= 318000000: return True
        if 868000000 <= freq_hz <= 868600000: return True
        return False

    def set_frequency(self, freq_hz: int) -> bool:
        self.frequency_hz = freq_hz
        f_xosc = 26000000
        freq_word = int((freq_hz * (1 << 16)) / f_xosc)
        self.registers[0x0D] = (freq_word >> 16) & 0xFF
        self.registers[0x0E] = (freq_word >> 8) & 0xFF
        self.registers[0x0F] = freq_word & 0xFF
        return True

    def transmit(self, protocol: str, key_hex: str, bit_length: int = 24, repeat: int = 3) -> Dict[str, Any]:
        allowed = self.is_frequency_allowed(self.frequency_hz)
        record = {
            "protocol": protocol, "key": key_hex, "bit_length": bit_length,
            "frequency_hz": self.frequency_hz, "repeat": repeat,
            "regional_allowed": allowed,
            "status": "TX_SUCCESS" if allowed else "TX_BLOCKED_BY_REGION"
        }
        self.tx_history.append(record)
        return record

    def transmit_raw(self, raw_samples: List[int]) -> Dict[str, Any]:
        allowed = self.is_frequency_allowed(self.frequency_hz)
        record = {
            "protocol": "RAW", "sample_count": len(raw_samples),
            "frequency_hz": self.frequency_hz, "regional_allowed": allowed,
            "status": "TX_SUCCESS" if allowed else "TX_BLOCKED_BY_REGION"
        }
        self.tx_history.append(record)
        return record

    def receive_packet(self, protocol: str = "Princeton", key_hex: str = "A1B2C3", freq_hz: int = 433920000) -> Dict[str, Any]:
        pkt = {
            "protocol": protocol, "key": key_hex, "frequency_hz": freq_hz,
            "rssi_dbm": self.rssi_dbm, "valid": True
        }
        self.rx_buffer.append(pkt)
        return pkt

    def read_reg(self, addr: int) -> int:
        return self.registers.get(addr & 0x3F, 0x00)

    def write_reg(self, addr: int, val: int):
        self.registers[addr & 0x3F] = val & 0xFF
