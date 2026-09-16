"""Deterministic host-side models for STM32WB services absent from the CPU engine.

The models deliberately expose *behaviour*, not protected device contents.  They
are suitable for firmware integration tests and replay, and never access USB or
debug hardware.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


class ModelError(ValueError):
    """Invalid or unsafe model operation."""


@dataclass(frozen=True)
class SafeDeviceInfo:
    """Non-secret InfoTable/option-byte view with immutable safe defaults."""

    flash_kib: int = 1024
    sram_kib: int = 256
    package: str = "STM32WB55RG"
    revision: str = "modeled"
    option_bytes: dict[str, int] = field(default_factory=lambda: {
        "RDP": 0xAA, "nBOOT0": 1, "nSWBOOT0": 0, "nBOOT1": 1,
    })

    @classmethod
    def from_json(cls, path: Path) -> "SafeDeviceInfo":
        raw = json.loads(Path(path).read_text())
        allowed = {"flash_kib", "sram_kib", "package", "revision", "option_bytes"}
        if set(raw) - allowed:
            raise ModelError("InfoTable fixture contains unsupported or identity-bearing fields")
        options = raw.get("option_bytes", {})
        if set(options) - {"RDP", "nBOOT0", "nSWBOOT0", "nBOOT1"}:
            raise ModelError("unsafe option-byte field")
        if options.get("RDP", 0xAA) != 0xAA:
            raise ModelError("only unlocked, non-destructive RDP modeling is supported")
        return cls(**raw)

    def write_option_byte(self, _name: str, _value: int) -> None:
        raise ModelError("option bytes are read-only in the emulator")


@dataclass
class HsemModel:
    owners: dict[int, int] = field(default_factory=dict)

    def take(self, semaphore: int, core: int) -> bool:
        if semaphore < 0 or semaphore >= 32 or core not in (1, 2):
            raise ModelError("invalid HSEM request")
        if semaphore in self.owners:
            return False
        self.owners[semaphore] = core
        return True

    def release(self, semaphore: int, core: int) -> bool:
        if self.owners.get(semaphore) != core:
            return False
        del self.owners[semaphore]
        return True


@dataclass
class IpccModel:
    """Six bidirectional IPCC channels with explicit send/receive semantics."""

    pending: dict[tuple[int, int], bytes] = field(default_factory=dict)

    def send(self, source: int, channel: int, payload: bytes) -> None:
        if source not in (1, 2) or not 1 <= channel <= 6:
            raise ModelError("invalid IPCC endpoint")
        key = (source, channel)
        if key in self.pending:
            raise ModelError("IPCC channel is busy")
        self.pending[key] = bytes(payload)

    def receive(self, destination: int, channel: int) -> bytes | None:
        if destination not in (1, 2) or not 1 <= channel <= 6:
            raise ModelError("invalid IPCC endpoint")
        return self.pending.pop((3 - destination, channel), None)


class Cpu2Service:
    """Functional command/reply facade for public FUS and radio status flows."""

    def __init__(self, replay: dict[str, Any] | None = None):
        replay = replay or {}
        self.mode = "radio" if replay.get("radio_alive", "true").lower() == "true" else "fus"
        self.replay = replay
        self.started = False

    def command(self, name: str, **params: Any) -> dict[str, Any]:
        if name == "start":
            self.started = True
            return {"status": "ok", "mode": self.mode}
        if name == "get_state":
            return {"status": "ok", "started": self.started, "mode": self.mode}
        if name == "get_version":
            prefix = "radio_fus_" if self.mode == "fus" else "radio_stack_"
            return {"status": "ok", "mode": self.mode,
                    "version": ".".join(str(self.replay.get(prefix + key, "0")) for key in ("major", "minor", "sub"))}
        if name == "ble_echo" and self.mode == "radio" and self.started:
            payload = params.get("payload", b"")
            if not isinstance(payload, bytes) or len(payload) > 251:
                return {"status": "invalid_parameter"}
            return {"status": "ok", "payload": payload}
        return {"status": "unsupported"}


@dataclass(frozen=True)
class PublicC2Firmware:
    """Auditable metadata for an upstream public CPU2 image.

    The binary is never mapped or executed: CPU2 behaviour is supplied by the
    deterministic service above.  This preserves provenance without pretending
    that the proprietary M0+ radio stack is emulated.
    """

    path: str
    sha256: str
    bytes: int
    classification: str = "public-upstream-c2-reference-only"
    executed: bool = False

    @classmethod
    def inspect(cls, path: Path) -> "PublicC2Firmware":
        path = Path(path).resolve()
        data = path.read_bytes()
        if len(data) < 1024 or len(data) > 1024 * 1024:
            raise ModelError("implausible public C2 firmware size")
        return cls(str(path), hashlib.sha256(data).hexdigest(), len(data))
