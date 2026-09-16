"""
Virtual MicroSD Card and SPI2 FAT Filesystem emulation for /ext.
"""

import os
import shutil
from typing import Dict, List, Optional, Tuple, Any

class VirtualSDCard:
    def __init__(self, root_path: Optional[str] = None):
        self.root_path = root_path
        if not self.root_path:
            base_proj = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../sd_card/ext"))
            self.root_path = base_proj
            
        os.makedirs(self.root_path, exist_ok=True)
        self.card_present = True
        self.card_type = "SDHC"
        self.capacity_bytes = 32 * 1024 * 1024 * 1024

    def _resolve_path(self, path: str) -> str:
        p = path.strip()
        if p.startswith("/ext/"): p = p[5:]
        elif p.startswith("/ext"): p = p[4:]
        elif p.startswith("/"): p = p[1:]
        clean_path = os.path.normpath(p)
        if clean_path.startswith(".."): clean_path = ""
        return os.path.join(self.root_path, clean_path)

    def list_dir(self, path: str = "/") -> List[Dict[str, Any]]:
        target = self._resolve_path(path)
        if not os.path.exists(target) or not os.path.isdir(target):
            return []
        results = []
        for name in sorted(os.listdir(target)):
            full_path = os.path.join(target, name)
            is_dir = os.path.isdir(full_path)
            size = os.path.getsize(full_path) if not is_dir else 0
            results.append({
                "name": name,
                "is_dir": is_dir,
                "size": size,
                "path": f"/ext/{os.path.relpath(full_path, self.root_path).replace(os.sep, '/')}"
            })
        return results

    def read_file(self, path: str) -> Optional[bytes]:
        target = self._resolve_path(path)
        if os.path.exists(target) and os.path.isfile(target):
            with open(target, "rb") as f:
                return f.read()
        return None

    def write_file(self, path: str, content: bytes) -> bool:
        target = self._resolve_path(path)
        os.makedirs(os.path.dirname(target), exist_ok=True)
        with open(target, "wb") as f:
            f.write(content)
        return True

    def delete_file(self, path: str) -> bool:
        target = self._resolve_path(path)
        if os.path.exists(target):
            if os.path.isdir(target): shutil.rmtree(target)
            else: os.remove(target)
            return True
        return False

    def make_dir(self, path: str) -> bool:
        target = self._resolve_path(path)
        os.makedirs(target, exist_ok=True)
        return True

    def get_fs_info(self) -> Dict[str, Any]:
        total_files = 0
        used_bytes = 0
        for root, _, files in os.walk(self.root_path):
            for f in files:
                total_files += 1
                used_bytes += os.path.getsize(os.path.join(root, f))
        return {
            "total_bytes": self.capacity_bytes,
            "free_bytes": max(0, self.capacity_bytes - used_bytes),
            "used_bytes": used_bytes,
            "total_files": total_files
        }
