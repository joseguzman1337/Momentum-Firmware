"""
Internal Flash Manager and persistent /int storage emulator.
"""

import os
import zlib
from typing import Dict, List, Optional
from ..models import FLASH_BASE, FLASH_END, DEFAULT_PROFILE

class InternalFlashManager:
    """Manages 1 MB flash and emulated /int persistent storage."""
    def __init__(self, fixtures_dir: Optional[str] = None):
        self.flash_size = FLASH_END - FLASH_BASE
        self.flash_memory = bytearray(b"\xFF" * self.flash_size)
        self.internal_files: Dict[str, bytes] = {}
        
        if fixtures_dir and os.path.exists(fixtures_dir):
            self.load_from_directory(fixtures_dir)
        else:
            default_fixture_path = os.path.join(os.path.dirname(__file__), "fixtures")
            if os.path.exists(default_fixture_path):
                self.load_from_directory(default_fixture_path)
            else:
                self._populate_defaults()

    def _populate_defaults(self):
        self.internal_files[".dolphin.state"] = b"\xd0\x018\x00" + b"\x00" * 36
        self.internal_files[".notification.settings"] = b"\x02\x00\x00\x00" + b"\x00" * 20
        self.internal_files[".region_data"] = b"\n\x02CO" + b"\x00" * 34
        self.internal_files[".bt.keys"] = b"\x18\x00" + b"\x00" * 10
        self.internal_files[".bt.settings"] = b"\x19\x00\x01\x00\x00\x00\x00\x00\x01"
        self.internal_files[".desktop.settings"] = b"\x17\n\x00\x00" + b"\x00" * 1048

    def load_from_directory(self, dir_path: str):
        for entry in os.listdir(dir_path):
            file_path = os.path.join(dir_path, entry)
            if os.path.isfile(file_path):
                with open(file_path, "rb") as f:
                    self.internal_files[entry] = f.read()

    def list_files(self) -> List[str]:
        return sorted(list(self.internal_files.keys()))

    def read_file(self, filename: str) -> Optional[bytes]:
        clean_name = os.path.basename(filename)
        return self.internal_files.get(clean_name)

    def write_file(self, filename: str, data: bytes):
        clean_name = os.path.basename(filename)
        self.internal_files[clean_name] = data

    def delete_file(self, filename: str) -> bool:
        clean_name = os.path.basename(filename)
        if clean_name in self.internal_files:
            del self.internal_files[clean_name]
            return True
        return False

    def get_crc32(self, filename: str) -> int:
        content = self.read_file(filename)
        if content is not None:
            return zlib.crc32(content) & 0xFFFFFFFF
        return 0

    def read_flash_address(self, addr: int, length: int = 4) -> bytes:
        offset = addr - FLASH_BASE
        if 0 <= offset <= self.flash_size - length:
            return bytes(self.flash_memory[offset:offset + length])
        return b"\xFF" * length

    def write_flash_address(self, addr: int, data: bytes) -> bool:
        offset = addr - FLASH_BASE
        if 0 <= offset <= self.flash_size - len(data):
            self.flash_memory[offset:offset + len(data)] = data
            return True
        return False
