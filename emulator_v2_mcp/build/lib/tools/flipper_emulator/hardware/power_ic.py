"""
Power Management & Fuel Gauge Emulation.
"""

from typing import Dict, Any

class PowerManagementController:
    def __init__(self, capacity_mah: int = 2100):
        self.capacity_mah = capacity_mah
        self.charge_percent = 98
        self.voltage_v = 4.18
        self.current_ma = -45
        self.temperature_c = 26.5
        self.health_percent = 99
        self.charging = False
        self.usb_power_connected = True

    def get_power_info(self) -> Dict[str, Any]:
        return {
            "charge_percent": self.charge_percent,
            "voltage_v": round(self.voltage_v, 2),
            "current_ma": self.current_ma,
            "capacity_mah": self.capacity_mah,
            "health_percent": self.health_percent,
            "temperature_c": self.temperature_c,
            "charging": self.charging,
            "usb_connected": self.usb_power_connected
        }

    def set_charge(self, percent: int):
        self.charge_percent = max(0, min(100, percent))
        self.voltage_v = 3.3 + (self.charge_percent / 100.0) * 0.9
