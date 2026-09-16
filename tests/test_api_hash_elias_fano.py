import csv
import random


def elf_hash(name: str) -> int:
    value = 0x1505
    for byte in name.encode():
        value = ((value << 5) + value + byte) & 0xFFFFFFFF
    return value


def encode(values):
    width = (0x100000000 // len(values)).bit_length() - 1
    low = bytearray((len(values) * width + 7) // 8)
    high = bytearray((len(values) + (0xFFFFFFFF >> width) + 8) // 8)
    for index, value in enumerate(values):
        for bit in range(width):
            if value & (1 << bit):
                position = index * width + bit
                low[position // 8] |= 1 << (position % 8)
        position = (value >> width) + index
        high[position // 8] |= 1 << (position % 8)
    return width, low, high


def decode_all(count, width, low, high):
    result = []
    high_position = 0
    for index in range(count):
        while not high[high_position // 8] & (1 << (high_position % 8)):
            high_position += 1
        low_value = 0
        for bit in range(width):
            position = index * width + bit
            low_value |= ((low[position // 8] >> (position % 8)) & 1) << bit
        result.append(((high_position - index) << width) | low_value)
        high_position += 1
    return result


def test_firmware_api_hashes_round_trip_and_negative_lookups():
    with open("targets/f7/api_symbols.csv", newline="") as source:
        rows = csv.DictReader(source)
        hashes = sorted(elf_hash(row["name"]) for row in rows if row["status"] == "+")

    assert len(hashes) == len(set(hashes))
    width, low, high = encode(hashes)
    decoded = decode_all(len(hashes), width, low, high)
    assert decoded == hashes

    present = set(decoded)
    random_source = random.Random(0xF17E)
    absent = [random_source.getrandbits(32) for _ in range(10000)]
    absent = [value for value in absent if value not in present]
    assert all(value not in present for value in absent)
    assert len(low) + len(high) < len(hashes) * 4
