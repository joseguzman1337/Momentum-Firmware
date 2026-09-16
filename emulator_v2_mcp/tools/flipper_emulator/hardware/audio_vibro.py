"""
Buzzer and Vibration Motor emulation.
"""

from typing import List, Dict, Any

class AudioVibroController:
    def __init__(self):
        self.buzzer_freq_hz = 0
        self.buzzer_volume = 1.0
        self.buzzer_active = False
        self.vibro_active = False
        self.led_r = 0
        self.led_g = 0
        self.led_b = 255
        self.sound_log: List[Dict[str, Any]] = []

    def play_tone(self, freq_hz: float, duration_ms: int = 100, volume: float = 1.0):
        self.buzzer_freq_hz = int(freq_hz)
        self.buzzer_volume = volume
        self.buzzer_active = True
        record = {"type": "tone", "frequency_hz": freq_hz, "duration_ms": duration_ms, "volume": volume}
        self.sound_log.append(record)
        if len(self.sound_log) > 50: self.sound_log.pop(0)

    def stop_tone(self):
        self.buzzer_active = False
        self.buzzer_freq_hz = 0

    def set_vibro(self, state: bool):
        self.vibro_active = state
        self.sound_log.append({"type": "vibro", "state": state})

    def set_led(self, r: int, g: int, b: int):
        self.led_r = max(0, min(255, r))
        self.led_g = max(0, min(255, g))
        self.led_b = max(0, min(255, b))

    def get_status(self) -> Dict[str, Any]:
        return {
            "buzzer": {"active": self.buzzer_active, "freq_hz": self.buzzer_freq_hz, "volume": self.buzzer_volume},
            "vibro": self.vibro_active,
            "led": {"r": self.led_r, "g": self.led_g, "b": self.led_b}
        }
