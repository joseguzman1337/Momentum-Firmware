"""
Virtual USB CDC-ACM Serial Interface & Flipper Interactive Command Line Shell (CLI).
"""

import time
import os
import shlex
from typing import List, Dict, Optional, Tuple, Any

class FlipperCLI:
    def __init__(self, emulator_ref: Any):
        self.emu = emulator_ref
        self.prompt = ">: "

    def execute_command(self, cmd_line: str) -> str:
        cmd_line = cmd_line.strip()
        if not cmd_line:
            return ""

        try:
            parts = shlex.split(cmd_line)
        except Exception:
            parts = cmd_line.split()

        cmd = parts[0].lower()
        args = parts[1:]

        if cmd in ("help", "?"):
            return self._cmd_help()
        elif cmd == "device_info":
            return self.emu.infotable.format_cli_output()
        elif cmd == "date":
            return self._cmd_date()
        elif cmd == "uptime":
            sec = int(self.emu.core.cycles / self.emu.core.clock_hz)
            return f"Uptime: {sec // 3600:02d}:{(sec % 3600) // 60:02d}:{sec % 60:02d}"
        elif cmd == "ps":
            return self._cmd_ps()
        elif cmd == "free":
            return self._cmd_free()
        elif cmd == "power":
            return self._cmd_power(args)
        elif cmd == "storage":
            return self._cmd_storage(args)
        elif cmd == "subghz":
            return self._cmd_subghz(args)
        elif cmd == "nfc":
            return self._cmd_nfc(args)
        elif cmd == "rfid":
            return self._cmd_rfid(args)
        elif cmd == "vibro":
            return self._cmd_vibro(args)
        elif cmd == "led":
            return self._cmd_led(args)
        elif cmd == "screen_dump":
            return self.emu.display.render_ascii()
        elif cmd in ("exit", "quit"):
            return "Bye!"
        else:
            return f"Command '{cmd}' not found. Type 'help' for available commands."

    def _cmd_help(self) -> str:
        return (
            "Welcome to Flipper Zero CLI (emulator-v2 Emulator v2)!\r\n"
            "Available commands:\r\n"
            "  device_info   - Display hardware, radio and firmware versions\r\n"
            "  date          - Get current RTC date and time\r\n"
            "  uptime        - Show system running time\r\n"
            "  ps            - Show running FuriOS threads\r\n"
            "  free          - Show SRAM heap memory statistics\r\n"
            "  power         - Power and battery info / reboot\r\n"
            "  storage       - File system operations (list, read, write, remove)\r\n"
            "  subghz        - Sub-GHz radio commands (tx, rx)\r\n"
            "  nfc           - NFC operations (read, emulate)\r\n"
            "  rfid          - 125kHz RFID operations (read, emulate)\r\n"
            "  vibro         - Control vibration motor\r\n"
            "  led           - Control notification RGB LED\r\n"
            "  screen_dump   - Print current ASCII framebuffer\r\n"
            "  help          - Display this help message\r\n"
        )

    def _cmd_date(self) -> str:
        now = time.localtime()
        return time.strftime("%Y-%m-%d %H:%M:%S", now)

    def _cmd_ps(self) -> str:
        lines = [
            "Thread Name       State   Prio  Stack Free",
            "----------------- ------- ----- ----------",
            "MainService       Running 10    2048",
            "GuiService        Blocked 12    1536",
            "DesktopApp        Blocked 8     3072",
            "StorageService    Blocked 15    2048",
            "CliService        Running 5     1024",
            "BtService         Blocked 10    2560",
            "SubGhzService     Blocked 10    3072",
            "PowerService      Blocked 6     1024"
        ]
        return "\r\n".join(lines)

    def _cmd_free(self) -> str:
        sram_total = self.emu.profile.sram1_size_bytes
        sram_free = sram_total - 48250
        return f"SRAM1: {sram_total} bytes total, {sram_free} bytes free, 48250 bytes used"

    def _cmd_power(self, args: List[str]) -> str:
        if args and args[0] == "info":
            info = self.emu.power.get_power_info()
            return (
                f"Charge: {info['charge_percent']}%\r\n"
                f"Voltage: {info['voltage_v']} V\r\n"
                f"Capacity: {info['capacity_mah']} mAh\r\n"
                f"Health: {info['health_percent']}%\r\n"
                f"Temperature: {info['temperature_c']} C\r\n"
                f"USB Power: {'Connected' if info['usb_connected'] else 'Disconnected'}"
            )
        elif args and args[0] == "reboot":
            self.emu.reset()
            return "Rebooting Flipper Zero..."
        return "Usage: power info | power reboot"

    def _cmd_storage(self, args: List[str]) -> str:
        if not args:
            return "Usage: storage <list|read|write|remove|info> [path]"
        sub = args[0].lower()
        if sub == "list":
            path = args[1] if len(args) > 1 else "/ext"
            if path.startswith("/int"):
                files = self.emu.flash_mgr.list_files()
                return "\r\n".join([f"  [FILE] {f}" for f in files])
            else:
                entries = self.emu.sd_card.list_dir(path)
                lines = []
                for e in entries:
                    kind = "[DIR]" if e["is_dir"] else f"[{e['size']} B]"
                    lines.append(f"  {kind} {e['name']}")
                return "\r\n".join(lines) if lines else "Empty directory"
        elif sub == "read":
            if len(args) < 2: return "Usage: storage read <path>"
            path = args[1]
            if path.startswith("/int"):
                content = self.emu.flash_mgr.read_file(path)
            else:
                content = self.emu.sd_card.read_file(path)
            if content is not None:
                try:
                    return content.decode("utf-8")
                except UnicodeDecodeError:
                    return content.hex()
            return "File not found"
        elif sub == "remove":
            if len(args) < 2: return "Usage: storage remove <path>"
            path = args[1]
            if path.startswith("/int"):
                ok = self.emu.flash_mgr.delete_file(path)
            else:
                ok = self.emu.sd_card.delete_file(path)
            return "Deleted" if ok else "Failed to delete"
        elif sub == "info":
            info = self.emu.sd_card.get_fs_info()
            return f"MicroSD: {info['used_bytes']} bytes used out of {info['total_bytes']} bytes ({info['total_files']} files)"
        return f"Unknown storage action: {sub}"

    def _cmd_subghz(self, args: List[str]) -> str:
        if not args:
            return "Usage: subghz <tx|rx|freq> [args]"
        action = args[0].lower()
        if action == "tx":
            freq = int(args[1]) if len(args) > 1 else self.emu.cc1101.frequency_hz
            self.emu.cc1101.set_frequency(freq)
            res = self.emu.cc1101.transmit("Princeton", "A1B2C3", 24)
            return f"Transmitted on {freq} Hz: Status {res['status']}"
        elif action == "rx":
            freq = int(args[1]) if len(args) > 1 else self.emu.cc1101.frequency_hz
            self.emu.cc1101.set_frequency(freq)
            res = self.emu.cc1101.receive_packet("Princeton", "A1B2C3", freq)
            return f"Listening on {freq} Hz... Received packet key: {res['key']} (RSSI: {res['rssi_dbm']} dBm)"
        elif action == "freq":
            if len(args) > 1:
                self.emu.cc1101.set_frequency(int(args[1]))
            return f"Current Sub-GHz frequency: {self.emu.cc1101.frequency_hz} Hz"
        return "Unknown subghz command"

    def _cmd_nfc(self, args: List[str]) -> str:
        if not args:
            return "Usage: nfc <read|emulate|stop>"
        action = args[0].lower()
        if action == "read":
            card = self.emu.nfc_rfid.read_nfc()
            return f"NFC Card Detected:\r\n  Type: {card['type']}\r\n  UID: {card['uid']}\r\n  ATQA: {card['atqa']}\r\n  SAK: {card['sak']}"
        elif action == "emulate":
            uid = args[1] if len(args) > 1 else "04 A1 B2 C3 D4 E5 F6"
            self.emu.nfc_rfid.emulate_nfc(uid)
            return f"Emulating NFC card with UID: {uid}"
        elif action == "stop":
            self.emu.nfc_rfid.stop_nfc_emulation()
            return "NFC emulation stopped."
        return "Unknown nfc command"

    def _cmd_rfid(self, args: List[str]) -> str:
        if not args:
            return "Usage: rfid <read|emulate|stop>"
        action = args[0].lower()
        if action == "read":
            tag = self.emu.nfc_rfid.read_rfid()
            return f"RFID 125kHz Tag Detected:\r\n  Protocol: {tag['protocol']}\r\n  Data: {tag['data']}"
        elif action == "emulate":
            data = args[1] if len(args) > 1 else "01 02 03 04 05"
            self.emu.nfc_rfid.emulate_rfid("EM4100", data)
            return f"Emulating EM4100 RFID tag: {data}"
        elif action == "stop":
            self.emu.nfc_rfid.stop_rfid_emulation()
            return "RFID emulation stopped."
        return "Unknown rfid command"

    def _cmd_vibro(self, args: List[str]) -> str:
        if args and args[0] in ("1", "on"):
            self.emu.audio_vibro.set_vibro(True)
            return "Vibration motor ON"
        else:
            self.emu.audio_vibro.set_vibro(False)
            return "Vibration motor OFF"

    def _cmd_led(self, args: List[str]) -> str:
        if len(args) >= 3:
            r, g, b = int(args[0]), int(args[1]), int(args[2])
            self.emu.audio_vibro.set_led(r, g, b)
            return f"LED color set to R:{r} G:{g} B:{b}"
        return "Usage: led <r 0-255> <g 0-255> <b 0-255>"
