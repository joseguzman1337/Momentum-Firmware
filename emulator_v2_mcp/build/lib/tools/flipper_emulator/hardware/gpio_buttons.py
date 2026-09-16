"""
GPIO, EXTI line controller, and physical button input management for Flipper Zero.
"""

from typing import List, Dict, Optional, Callable
import time
from ..models import ButtonKey, InputType, InputEvent
from .st7567 import ST7567Display

class ButtonGPIOController:
    def __init__(self, display: Optional[ST7567Display] = None):
        self.display = display
        self.event_queue: List[InputEvent] = []
        self.button_states: Dict[ButtonKey, bool] = {
            ButtonKey.UP: False,
            ButtonKey.DOWN: False,
            ButtonKey.LEFT: False,
            ButtonKey.RIGHT: False,
            ButtonKey.OK: False,
            ButtonKey.BACK: False,
        }
        self.menu_items = ["Sub-GHz", "125kHz RFID", "NFC", "Infrared", "iButton", "BadUSB"]
        self.selected_menu_idx = 0
        self.current_screen = "desktop"

    def send_input(self, key: ButtonKey, input_type: InputType) -> InputEvent:
        if isinstance(key, str): key = ButtonKey(key.upper())
        if isinstance(input_type, str): input_type = InputType(input_type.upper())

        event = InputEvent(key=key, type=input_type, timestamp=time.time())
        self.event_queue.append(event)
        
        if input_type in (InputType.PRESS, InputType.SHORT, InputType.LONG):
            self.button_states[key] = True
            self._handle_navigation(key, input_type)
        elif input_type == InputType.RELEASE:
            self.button_states[key] = False

        return event

    def _handle_navigation(self, key: ButtonKey, input_type: InputType):
        if not self.display: return

        if self.current_screen == "desktop":
            if key == ButtonKey.DOWN:
                self.selected_menu_idx = (self.selected_menu_idx + 1) % len(self.menu_items)
                self._redraw_desktop()
            elif key == ButtonKey.UP:
                self.selected_menu_idx = (self.selected_menu_idx - 1) % len(self.menu_items)
                self._redraw_desktop()
            elif key == ButtonKey.OK:
                selected = self.menu_items[self.selected_menu_idx]
                self._show_app_screen(selected)
            elif key == ButtonKey.LEFT:
                self._show_passport_screen()
        else:
            if key == ButtonKey.BACK:
                self.current_screen = "desktop"
                self._redraw_desktop()

    def _redraw_desktop(self):
        self.display.clear(0)
        self.display.draw_rect(0, 0, 128, 10, color=1, fill=True)
        self.display.draw_text(2, 1, "emulator-v2", color=0)
        self.display.draw_text(60, 1, "BLE", color=0)
        self.display.draw_text(92, 1, "98%", color=0)
        
        self.display.draw_rect(10, 18, 48, 38, color=1, fill=False)
        self.display.draw_text(16, 26, "( ^_^ )", color=1)
        self.display.draw_text(14, 38, "Lv.3 Happy", color=1)
        
        y_positions = [16, 26, 36, 46, 56]
        start_idx = max(0, min(self.selected_menu_idx - 2, len(self.menu_items) - 5))
        for i in range(5):
            idx = start_idx + i
            if idx < len(self.menu_items):
                prefix = "> " if idx == self.selected_menu_idx else "  "
                self.display.draw_text(68, y_positions[i], prefix + self.menu_items[idx][:9], color=1)

    def _show_app_screen(self, app_name: str):
        self.current_screen = app_name.lower()
        self.display.clear(0)
        self.display.draw_rect(0, 0, 128, 10, color=1, fill=True)
        self.display.draw_text(2, 1, app_name, color=0)
        self.display.draw_text(10, 20, f"App: {app_name}", color=1)
        self.display.draw_text(10, 32, "Read / Emulate", color=1)
        self.display.draw_text(10, 48, "[OK] Run  [BACK] Exit", color=1)

    def _show_passport_screen(self):
        self.current_screen = "passport"
        self.display.clear(0)
        self.display.draw_rect(0, 0, 128, 10, color=1, fill=True)
        self.display.draw_text(2, 1, "Flipper Passport", color=0)
        self.display.draw_text(8, 18, "Name: emulator-v2", color=1)
        self.display.draw_text(8, 28, "Model: F7B9C6", color=1)
        self.display.draw_text(8, 38, "Region: CO (4)", color=1)
        self.display.draw_text(8, 48, "Mood: Joy / Lv 3", color=1)
