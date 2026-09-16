from __future__ import annotations

from pathlib import Path

from ..internal_flash import InternalFlashStore
from .protocol import delimited, field_bytes, field_varint, fields


def nested_value(payload: bytes, number: int) -> bytes | None:
    return next((value for field, wire, value in fields(payload) if field == number and wire == 2), None)


class VirtualFlipperRpc:
    """Clean-room handler for the documented Flipper PB.Main wire contract."""

    def __init__(self, flash_image: Path, framebuffer: bytes | None = None):
        self.flash = InternalFlashStore(flash_image)
        self.framebuffer = framebuffer or bytes(1024)

    @staticmethod
    def main(command_id: int, content_field: int, content: bytes = b"", *, has_next: bool = False, status: int = 0) -> bytes:
        body = field_varint(1, command_id)
        if status:
            body += field_varint(2, status)
        if has_next:
            body += field_varint(3, 1)
        body += field_bytes(content_field, content)
        return delimited(body)

    def handle(self, message: bytes) -> list[bytes]:
        parsed = fields(message)
        command_id = int(next((value for number, wire, value in parsed if number == 1 and wire == 0), 0))
        content = next(((number, value) for number, wire, value in parsed if wire == 2 and number != 1), None)
        if content is None:
            return [self.main(command_id, 4, status=2)]
        tag, payload = content
        assert isinstance(payload, bytes)
        if tag == 5:  # System.PingRequest -> PingResponse
            return [self.main(command_id, 6, payload)]
        if tag == 32:  # sanitized DeviceInfo stream
            properties = (("hardware_model", "Flipper Zero"), ("hardware_target", "7"), ("firmware_api", "88.2"), ("radio_alive", "true"))
            return [self.main(command_id, 33, field_bytes(1, key.encode()) + field_bytes(2, value.encode()), has_next=index < len(properties) - 1) for index, (key, value) in enumerate(properties)]
        if tag == 39:  # protobuf version
            return [self.main(command_id, 40, field_varint(1, 0) + field_varint(2, 25))]
        if tag == 20:  # screen stream acknowledge + frame
            frame = field_bytes(1, self.framebuffer)
            return [self.main(command_id, 4), self.main(0, 22, frame)]
        if tag == 21:  # stop screen stream
            return [self.main(command_id, 4)]
        if tag == 28:  # storage info
            return [self.main(command_id, 29, field_varint(1, 128 * 1024) + field_varint(2, 96 * 1024))]
        if tag == 7:  # storage list /int
            path = nested_value(payload, 1)
            if path != b"/int":
                return [self.main(command_id, 4, status=10)]
            entries = []
            for name, size in self.flash.list():
                file_message = field_bytes(2, name.encode()) + field_varint(3, size)
                entries.append(field_bytes(1, file_message))
            return [self.main(command_id, 8, b"".join(entries))]
        if tag == 9:  # storage read
            path = nested_value(payload, 1)
            try:
                value = self.flash.read(path.decode()) if path else b""
            except (KeyError, ValueError):
                return [self.main(command_id, 4, status=7)]
            file_message = field_varint(3, len(value)) + field_bytes(4, value)
            return [self.main(command_id, 10, field_bytes(1, file_message))]
        return [self.main(command_id, 4, status=3)]
