"""
Unified Flipper Zero Emulator v2 Engine.
"""

from typing import Optional, Dict, Any
from .models import DEFAULT_PROFILE, FlipperProfile, ButtonKey, InputType, InputEvent
from .hardware.cortex_m4 import CortexM4Core
from .hardware.stm32wb55 import STM32WB55Bus
from .hardware.nvic import NVICController
from .hardware.systick_dwt import SysTickTimer, DWTCounter
from .hardware.rcc_rtc import RCCController, RTCController
from .hardware.hsem_ipcc import HSEMController, IPCCController
from .hardware.wireless_cpu2 import WirelessCPU2Controller
from .hardware.st7567 import ST7567Display
from .hardware.gpio_buttons import ButtonGPIOController
from .hardware.spi_sd import VirtualSDCard
from .hardware.audio_vibro import AudioVibroController
from .hardware.cc1101 import CC1101Transceiver
from .hardware.st25r3916 import NFCRFIDController
from .hardware.power_ic import PowerManagementController
from .internal_flash.flash_manager import InternalFlashManager
from .internal_flash.otp import FlipperOTP, OptionBytes
from .internal_flash.infotable import InfoTable
from .usb.cdc_acm import FlipperCLI
from .usb.rpc_protobuf import FlipperRPCHandler
from .usb.pty_transport import VirtualPTYTransport

class FlipperZeroEmulator:
    def __init__(self, profile: Optional[FlipperProfile] = None, sd_card_path: Optional[str] = None):
        self.profile = profile or DEFAULT_PROFILE
        
        self.flash_mgr = InternalFlashManager()
        self.otp = FlipperOTP(self.profile)
        self.option_bytes = OptionBytes()
        self.infotable = InfoTable(self.profile)
        
        self.bus = STM32WB55Bus(self.flash_mgr)
        
        self.core = CortexM4Core(clock_hz=self.profile.cpu1_clock_mhz * 1000000)
        self.nvic = NVICController(self.core)
        self.systick = SysTickTimer(self.core)
        self.dwt = DWTCounter(self.core)
        
        self.rcc = RCCController()
        self.rtc = RTCController()
        self.hsem = HSEMController()
        self.ipcc = IPCCController()
        self.cpu2 = WirelessCPU2Controller(self.profile)
        
        self.display = ST7567Display()
        self.buttons = ButtonGPIOController(self.display)
        self.audio_vibro = AudioVibroController()
        
        self.sd_card = VirtualSDCard(sd_card_path)
        self.cc1101 = CC1101Transceiver(region_code=self.profile.hardware_region)
        self.nfc_rfid = NFCRFIDController()
        self.power = PowerManagementController(capacity_mah=self.profile.battery_capacity_mah)
        
        self.cli = FlipperCLI(self)
        self.rpc = FlipperRPCHandler(self)
        self.pty = VirtualPTYTransport(on_receive_callback=self._handle_serial_in)
        
        self._map_peripherals()
        self.reset()

    def _map_peripherals(self):
        self.bus.register_peripheral(0x58000000, self.rcc.read_register, self.rcc.write_register)
        self.bus.register_peripheral(0x40002800, self.rtc.read_register, self.rtc.write_register)
        self.bus.register_peripheral(0x58001400, self.hsem.read_register, self.hsem.write_register)
        self.bus.register_peripheral(0x58000C00, self.ipcc.read_register, self.ipcc.write_register)
        self.bus.register_peripheral(0xE000E100, self.nvic.read_register, self.nvic.write_register)
        self.bus.register_peripheral(0xE000E010, self.systick.read_register, self.systick.write_register)
        self.bus.register_peripheral(0xE0001000, self.dwt.read_register, self.dwt.write_register)

    def reset(self):
        initial_sp = 0x20030000
        initial_pc = 0x08000101
        self.core.reset(initial_sp=initial_sp, initial_pc=initial_pc)
        self.nvic.set_vtor(0x08000000)
        self.display._init_default_gui()
        self.audio_vibro.set_led(0, 255, 0)
        self.audio_vibro.play_tone(1046.5, duration_ms=80)

    def step(self, cycles: int = 1000):
        self.core.step(cycles)
        self.systick.step(cycles)

    def press_button(self, key: str, input_type: str = "SHORT") -> InputEvent:
        return self.buttons.send_input(ButtonKey(key.upper()), InputType(input_type.upper()))

    def get_screen_ascii(self) -> str:
        return self.display.render_ascii()

    def get_screen_base64_pbm(self) -> str:
        return self.display.to_base64_pbm()

    def run_cli_command(self, cmd: str) -> str:
        return self.cli.execute_command(cmd)

    def _handle_serial_in(self, data: bytes):
        try:
            text = data.decode("utf-8", errors="replace")
            resp = self.cli.execute_command(text)
            if resp:
                self.pty.write((resp + "\r\n>: ").encode("utf-8"))
        except Exception:
            pass

    def get_state_summary(self) -> Dict[str, Any]:
        return {
            "profile": {
                "name": self.profile.device_name,
                "variant": self.profile.production_variant,
                "model": self.profile.hardware_model,
                "color": "White" if self.profile.hardware_color == 2 else "Black",
                "region": self.profile.hardware_region_name,
            },
            "cpu": self.core.dump_state(),
            "power": self.power.get_power_info(),
            "radio_cpu2": self.cpu2.get_status(),
            "subghz_frequency": self.cc1101.frequency_hz,
            "storage_ext": self.sd_card.get_fs_info(),
            "internal_files": self.flash_mgr.list_files(),
            "display": {
                "width": self.display.width,
                "height": self.display.height,
                "inverted": self.display.inverted,
                "contrast": self.display.contrast
            }
        }
