"""
Sanitised InfoTable representation for Furi HAL.
"""

from typing import Dict, Any, Optional
from ..models import DEFAULT_PROFILE, FlipperProfile

class InfoTable:
    """Provides memory-mapped read-only system information according to Furi HAL format."""
    def __init__(self, profile: Optional[FlipperProfile] = None):
        self.profile = profile or DEFAULT_PROFILE

    def get_dict(self) -> Dict[str, Any]:
        return {
            "device_name": self.profile.device_name,
            "hardware_model": self.profile.hardware_model,
            "production_variant": self.profile.production_variant,
            "hardware_version": self.profile.hardware_ver,
            "hardware_target": self.profile.hardware_target,
            "hardware_body": self.profile.hardware_body,
            "hardware_connect": self.profile.hardware_connect,
            "hardware_display": self.profile.hardware_display,
            "hardware_color": self.profile.hardware_color,
            "hardware_region": self.profile.hardware_region,
            "hardware_region_name": self.profile.hardware_region_name,
            "firmware_version": self.profile.firmware_version,
            "firmware_commit": self.profile.firmware_commit,
            "firmware_branch": self.profile.firmware_branch,
            "firmware_origin": self.profile.firmware_origin,
            "radio_stack_version": self.profile.wireless_stack_version,
            "radio_fus_version": self.profile.wireless_fus_version,
            "protobuf_version_major": self.profile.protobuf_version_major,
            "protobuf_version_minor": self.profile.protobuf_version_minor,
            "device_info_major": self.profile.device_info_major,
            "device_info_minor": self.profile.device_info_minor,
            "usb_vid": f"0x{self.profile.usb_vid:04X}",
            "usb_pid": f"0x{self.profile.usb_pid:04X}",
            "usb_serial": self.profile.usb_serial,
        }

    def format_cli_output(self) -> str:
        d = self.get_dict()
        lines = [
            f"hardware_model             : {d['hardware_model']}",
            f"hardware_variant           : {d['production_variant']}",
            f"hardware_name              : {d['device_name']}",
            f"hardware_ver               : {d['hardware_version']}",
            f"hardware_target            : {d['hardware_target']}",
            f"hardware_body              : {d['hardware_body']}",
            f"hardware_connect           : {d['hardware_connect']}",
            f"hardware_display           : {d['hardware_display']}",
            f"hardware_color             : {d['hardware_color']}",
            f"hardware_region            : {d['hardware_region']}",
            f"hardware_region_name       : {d['hardware_region_name']}",
            f"hardware_otp_ver           : 2",
            f"firmware_version           : {d['firmware_version']}",
            f"firmware_commit            : {d['firmware_commit']}",
            f"firmware_branch            : {d['firmware_branch']}",
            f"firmware_origin            : {d['firmware_origin']}",
            f"radio_alive                : true",
            f"radio_fus_ver              : {d['radio_fus_version']}",
            f"radio_stack_ver            : {d['radio_stack_version']}",
            f"radio_stack_type           : 1",
            f"device_info_major          : {d['device_info_major']}",
            f"device_info_minor          : {d['device_info_minor']}",
            f"protobuf_version_major     : {d['protobuf_version_major']}",
            f"protobuf_version_minor     : {d['protobuf_version_minor']}",
        ]
        return "\r\n".join(lines)
