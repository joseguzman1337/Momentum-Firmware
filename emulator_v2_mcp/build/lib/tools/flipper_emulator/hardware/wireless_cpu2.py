"""
CPU2 (Cortex-M0+) Coprocessor, FUS, and Wireless Radio Stack deterministic emulation.
"""

from typing import Dict, Any, Optional
from ..models import DEFAULT_PROFILE, FlipperProfile

class WirelessCPU2Controller:
    def __init__(self, profile: Optional[FlipperProfile] = None):
        self.profile = profile or DEFAULT_PROFILE
        self.fus_version = self.profile.wireless_fus_version
        self.stack_version = self.profile.wireless_stack_version
        self.stack_type = 1
        self.state = 1
        self.radio_alive = True
        self.ble_mac_address = "48:B6:20:A1:B2:C3"
        self.ble_connected = False
        self.ble_advertising = True
        self.transmitted_packets = 0
        self.received_packets = 0

    def get_status(self) -> Dict[str, Any]:
        return {
            "radio_alive": self.radio_alive,
            "fus_version": self.fus_version,
            "stack_version": self.stack_version,
            "stack_type": self.stack_type,
            "ble_mac": self.ble_mac_address,
            "ble_advertising": self.ble_advertising,
            "ble_connected": self.ble_connected,
            "tx_packets": self.transmitted_packets,
            "rx_packets": self.received_packets,
        }

    def process_mailbox_command(self, opcode: int, payload: bytes) -> bytes:
        if opcode == 0xFD01:
            return bytes([0x00, 0x01, 0x02, 0x00])
        elif opcode == 0xFC00:
            return bytes([0x00, 0x01, 0x14, 0x00])
        elif opcode == 0x1009:
            return b"\x00\xC3\xB2\xA1\x20\xB6\x48"
        elif opcode == 0x2006:
            self.ble_advertising = True
            return b"\x00"
        return b"\x00"
