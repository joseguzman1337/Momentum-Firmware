import importlib.util
import base64
import json
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
location = ROOT / "scripts" / "verify_emulator_v2_mcp.py"
spec = importlib.util.spec_from_file_location("verify_emulator_v2_mcp", location)
module = importlib.util.module_from_spec(spec)
assert spec.loader
spec.loader.exec_module(module)


class FullSpecAuditTests(unittest.TestCase):
    def test_missing_surfaces_are_reported(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "spec.json"
            path.write_text(json.dumps({"firmware": "missing", "output": tmp}))
            _, errors = module.audit_full_spec(path)
            self.assertTrue(any("oracle_snapshot" in error for error in errors))
            self.assertTrue(any("virtual_usb" in error for error in errors))

    def test_repository_full_spec_contract(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            path = root / "spec.json"
            path.write_text(json.dumps({
                "firmware": str(ROOT / "build/f7-firmware-C/firmware.bin"),
                "output": str(root / "out"),
                "max_instructions": 250_000_000,
                "live_control": True,
                "virtual_usb": True,
                "sd_tree": str(ROOT / ".ai/fz-emulator/sd-fixture"),
                "oracle_snapshot": str(ROOT / ".ai/fz-emulator/snapshot"),
                "internal_flash_image": str(root / "internal-flash.json"),
            }))
            _, errors = module.audit_full_spec(path)
            self.assertEqual(errors, [])

    def test_internal_flash_reopens_without_drift(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "int.json"
            path.write_text(json.dumps({"schema": 1, "sanitized": True, "files": {"/int/.settings": base64.b64encode(b"stable").decode()}}))
            result = module.verify_internal_flash_persistence(path)
            self.assertTrue(result["valid"])
            self.assertTrue(result["reopen_equal"])
            self.assertEqual(result["bytes"], 6)


if __name__ == "__main__": unittest.main()
