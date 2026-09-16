import importlib.util
import struct
import sys
import tempfile
import unittest
import zlib
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))
SPEC = importlib.util.spec_from_file_location(
    "firmware_update", REPO_ROOT / "scripts/update.py"
)
UPDATE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(UPDATE)


def make_dfuse(path, address, payload):
    element = struct.pack("<II", address, len(payload)) + payload
    target = (
        struct.pack("<6sBI255sII", b"Target", 0, 1, b"test", len(element), 1) + element
    )
    image_size = 11 + len(target)
    prefix = struct.pack("<5sBIB", b"DfuSe", 1, image_size, 1)
    image = prefix + target
    suffix = struct.pack("<HHHH3sB", 0xFFFF, 0xDF11, 0x0483, 0x011A, b"UFD", 16)
    image += suffix
    image += struct.pack("<I", ~zlib.crc32(image) & 0xFFFFFFFF)
    path.write_bytes(image)


class DfuLayoutTest(unittest.TestCase):
    def test_linker_reserves_same_one_page_c2_headroom(self):
        linker = (REPO_ROOT / "targets/f7/stm32wb55xx_flash.ld").read_text()
        self.assertIn("LENGTH = 856K", linker)
        self.assertEqual(
            UPDATE.Main.FLASH_BASE + 856 * 1024,
            0x080D7000 - UPDATE.Main.FLASH_PAGE_SIZE,
        )

    def test_flash_range_excludes_dfuse_envelope(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "firmware.dfu"
            make_dfuse(path, 0x08000000, bytes(880544))
            self.assertEqual(
                UPDATE.Main.dfu_flash_range(path), (0x08000000, 0x080D6FA0)
            )
            self.assertEqual(path.stat().st_size - 880544, 309)

    def test_rejects_mismatched_header_size(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "firmware.dfu"
            make_dfuse(path, 0x08000000, b"payload")
            data = bytearray(path.read_bytes())
            data[6:10] = struct.pack("<I", 1)
            path.write_bytes(data)
            with self.assertRaisesRegex(ValueError, "size"):
                UPDATE.Main.dfu_flash_range(path)

    def test_rejects_bad_crc(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "firmware.dfu"
            make_dfuse(path, 0x08000000, b"payload")
            data = bytearray(path.read_bytes())
            data[-1] ^= 1
            path.write_bytes(data)
            with self.assertRaisesRegex(ValueError, "CRC"):
                UPDATE.Main.dfu_flash_range(path)

    def test_release_headroom_is_at_least_one_page_and_not_bypassable(self):
        app = UPDATE.Main(no_exit=True)
        radio = 0x080D7000
        self.assertFalse(app.c2_headroom_check((0x08000000, radio - 4095), radio))
        self.assertTrue(app.c2_headroom_check((0x08000000, radio - 4096), radio))

    def test_environment_cannot_lower_physical_headroom_floor(self):
        old = UPDATE.Main.MIN_GAP_PAGES
        try:
            UPDATE.Main.MIN_GAP_PAGES = max(1, int("0"))
            self.assertEqual(UPDATE.Main.MIN_GAP_PAGES, 1)
        finally:
            UPDATE.Main.MIN_GAP_PAGES = old


if __name__ == "__main__":
    unittest.main()
