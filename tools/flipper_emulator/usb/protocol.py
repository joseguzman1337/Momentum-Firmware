from __future__ import annotations


def varint(value: int) -> bytes:
    result = bytearray()
    while True:
        byte = value & 0x7F
        value >>= 7
        result.append(byte | (0x80 if value else 0))
        if not value:
            return bytes(result)


def read_varint(data: bytes | bytearray, offset: int = 0) -> tuple[int, int]:
    value = 0
    for shift in range(0, 70, 7):
        if offset >= len(data):
            raise EOFError
        byte = data[offset]
        offset += 1
        value |= (byte & 0x7F) << shift
        if not byte & 0x80:
            return value, offset
    raise ValueError("oversized varint")


def field_varint(number: int, value: int) -> bytes:
    return varint(number << 3) + varint(value)


def field_bytes(number: int, value: bytes) -> bytes:
    return varint((number << 3) | 2) + varint(len(value)) + value


def fields(data: bytes) -> list[tuple[int, int, int | bytes]]:
    result = []
    offset = 0
    while offset < len(data):
        tag, offset = read_varint(data, offset)
        number, wire = tag >> 3, tag & 7
        if wire == 0:
            value, offset = read_varint(data, offset)
        elif wire == 2:
            size, offset = read_varint(data, offset)
            value = data[offset:offset + size]
            if len(value) != size:
                raise EOFError
            offset += size
        else:
            raise ValueError(f"unsupported wire type {wire}")
        result.append((number, wire, value))
    return result


class DelimitedDecoder:
    def __init__(self):
        self.buffer = bytearray()

    def feed(self, data: bytes) -> list[bytes]:
        self.buffer.extend(data)
        messages = []
        while self.buffer:
            try:
                size, offset = read_varint(self.buffer)
            except EOFError:
                break
            if len(self.buffer) < offset + size:
                break
            messages.append(bytes(self.buffer[offset:offset + size]))
            del self.buffer[:offset + size]
        return messages


def delimited(message: bytes) -> bytes:
    return varint(len(message)) + message
