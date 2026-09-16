import importlib.util
import struct
import sys
import tempfile
import unittest
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
SPEC = importlib.util.spec_from_file_location(
    "update_package_report", ROOT / "scripts/update_package_report.py"
)
REPORT = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(REPORT)


def dfu(path: Path, size: int):
    payload = bytes(size)
    element = struct.pack("<II", 0x08000000, size) + payload
    target = (
        struct.pack("<6sBI255sII", b"Target", 0, 1, b"test", len(element), 1) + element
    )
    image = struct.pack("<5sBIB", b"DfuSe", 1, 11 + len(target), 1) + target
    image += struct.pack("<HHHH3sB", 0xFFFF, 0xDF11, 0x0483, 0x011A, b"UFD", 16)
    image += struct.pack("<I", ~zlib.crc32(image) & 0xFFFFFFFF)
    path.write_bytes(image)


class PackageReportTest(unittest.TestCase):
    def test_reports_exact_ready_layout_and_hashes(self):
        with tempfile.TemporaryDirectory() as directory:
            package = Path(directory) / "pkg"
            package.mkdir()
            dfu(package / "firmware.dfu", 0xD6000)
            for name in ("updater.bin", "radio.bin", "resources.tar.gz"):
                (package / name).write_bytes(name.encode())
            (package / "update.fuf").write_text(
                "Filetype: Flipper firmware upgrade configuration\n"
                "Version: 2\nInfo: test\nTarget: 7\nLoader: updater.bin\n"
                "Firmware: firmware.dfu\nRadio: radio.bin\nRadio address: 00 70 0D 08\n"
                "Resources: resources.tar.gz\n",
                encoding="utf-8",
            )
            result = REPORT.audit(package)
            self.assertEqual(result["firmware"]["headroom_bytes"], 4096)
            self.assertEqual(result["firmware"]["required_headroom_bytes"], 4096)
            self.assertEqual(result["firmware"]["cpu1_payload_bytes"], 0xD6000)
            self.assertEqual(
                result["firmware"]["cpu1_capacity_before_guard_bytes"], 0xD6000
            )
            self.assertEqual(result["firmware"]["cpu1_free_bytes"], 0)
            self.assertTrue(result["firmware"]["layout_ready"])
            self.assertEqual(len(result["files"]["firmware.dfu"]["sha256"]), 64)


if __name__ == "__main__":
    unittest.main()
