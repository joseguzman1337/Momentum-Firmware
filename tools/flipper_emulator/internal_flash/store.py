from __future__ import annotations

import base64
import json
import os
import re
import tempfile
from pathlib import Path, PurePosixPath

DENIED = re.compile(r"(?i)(\.bt|pair|key|secret|token|uid|serial|dolphin)")
DEFAULTS = {
    "/int/.notification.settings": bytes(24),
    "/int/.expansion.settings": bytes(9),
    "/int/.desktop.settings": bytes(1040),
    "/int/.region_data": b"Filetype: Flipper Region File\nVersion: 1\nCountry: 00\n",
    "/int/.momentum_firstboot.flag": b"",
}


class InternalFlashStore:
    """Small atomic JSON-backed /int image with no device-derived identity."""

    def __init__(self, image: Path, defaults: dict[str, bytes] | None = None):
        self.image = Path(image)
        image_exists = self.image.exists()
        self.files = dict(DEFAULTS if defaults is None else defaults)
        if image_exists:
            raw = json.loads(self.image.read_text(encoding="utf-8"))
            if raw.get("schema") != 1:
                raise ValueError("unsupported internal flash image")
            self.files = {path: base64.b64decode(data) for path, data in raw["files"].items()}
        self._validate_all()
        if not image_exists:
            self.save()

    @staticmethod
    def validate_path(path: str) -> None:
        pure = PurePosixPath(path)
        if not path.startswith("/int/") or ".." in pure.parts or DENIED.search(path):
            raise ValueError("unsafe internal flash path")

    def _validate_all(self) -> None:
        for path in self.files:
            self.validate_path(path)

    def read(self, path: str) -> bytes:
        self.validate_path(path)
        return self.files[path]

    def write(self, path: str, data: bytes) -> None:
        self.validate_path(path)
        self.files[path] = bytes(data)
        self.save()

    def list(self, directory: str = "/int") -> list[tuple[str, int]]:
        prefix = directory.rstrip("/") + "/"
        return sorted((path[len(prefix):], len(data)) for path, data in self.files.items() if path.startswith(prefix) and "/" not in path[len(prefix):])

    def save(self) -> None:
        self.image.parent.mkdir(parents=True, exist_ok=True)
        payload = {"schema": 1, "sanitized": True, "files": {path: base64.b64encode(data).decode("ascii") for path, data in sorted(self.files.items())}}
        handle, temporary = tempfile.mkstemp(prefix=".internal-flash-", dir=self.image.parent)
        try:
            with os.fdopen(handle, "w", encoding="utf-8") as stream:
                json.dump(payload, stream, indent=2, sort_keys=True)
                stream.write("\n")
                stream.flush()
                os.fsync(stream.fileno())
            os.replace(temporary, self.image)
        finally:
            if os.path.exists(temporary):
                os.unlink(temporary)
