"""
Flipper Zero RPC Protobuf Protocol Engine.
"""

from typing import Dict, Any, List, Optional, Tuple

class FlipperRPCHandler:
    def __init__(self, emulator_ref: Any):
        self.emu = emulator_ref
        self.session_active = False

    def handle_ping(self, command_id: int = 1) -> Dict[str, Any]:
        return {
            "command_id": command_id,
            "status": "OK",
            "type": "system_ping_response"
        }

    def handle_device_info(self, command_id: int = 2) -> List[Tuple[str, str]]:
        info = self.emu.infotable.get_dict()
        return [
            ("hardware_model", str(info["hardware_model"])),
            ("hardware_name", str(info["device_name"])),
            ("hardware_ver", str(info["hardware_version"])),
            ("hardware_target", str(info["hardware_target"])),
            ("hardware_body", str(info["hardware_body"])),
            ("hardware_connect", str(info["hardware_connect"])),
            ("hardware_display", str(info["hardware_display"])),
            ("hardware_color", str(info["hardware_color"])),
            ("hardware_region", str(info["hardware_region"])),
            ("hardware_region_name", str(info["hardware_region_name"])),
            ("hardware_otp_ver", "2"),
            ("firmware_version", str(info["firmware_version"])),
            ("firmware_commit", str(info["firmware_commit"])),
            ("firmware_branch", str(info["firmware_branch"])),
            ("firmware_origin", str(info["firmware_origin"])),
            ("radio_alive", "true"),
            ("radio_fus_ver", str(info["radio_fus_version"])),
            ("radio_stack_ver", str(info["radio_stack_version"])),
            ("protobuf_version_major", str(info["protobuf_version_major"])),
            ("protobuf_version_minor", str(info["protobuf_version_minor"])),
        ]

    def handle_screen_frame(self) -> bytes:
        return self.emu.display.get_framebuffer()

    def handle_storage_list(self, path: str = "/ext") -> List[Dict[str, Any]]:
        if path.startswith("/int"):
            files = self.emu.flash_mgr.list_files()
            return [{"name": f, "type": "FILE", "size": len(self.emu.flash_mgr.read_file(f) or b"")} for f in files]
        else:
            entries = self.emu.sd_card.list_dir(path)
            return [
                {"name": e["name"], "type": "DIR" if e["is_dir"] else "FILE", "size": e["size"]}
                for e in entries
            ]

    def handle_storage_read(self, path: str) -> Optional[bytes]:
        if path.startswith("/int"):
            return self.emu.flash_mgr.read_file(path)
        return self.emu.sd_card.read_file(path)

    def handle_storage_write(self, path: str, data: bytes) -> bool:
        if path.startswith("/int"):
            self.emu.flash_mgr.write_file(path, data)
            return True
        return self.emu.sd_card.write_file(path, data)
