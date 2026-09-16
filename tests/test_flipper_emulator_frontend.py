import importlib.util
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "tools" / "flipper_emulator" / "flipper_emulator.py"


class FlipperEmulatorFrontendTest(unittest.TestCase):
    def test_capability_roles_are_explicit(self):
        data = json.loads(MODULE_PATH.with_name("capabilities.json").read_text())
        self.assertEqual(
            {v["role"] for v in data["backends"].values()},
            {"functional", "cross-check", "hardware-oracle"},
        )
        self.assertIn(
            "cpu2 is a boot-boundary stub",
            data["backends"]["native"]["limitations"],
        )

    def test_frontend_resolves_inside_workspace(self):
        spec = importlib.util.spec_from_file_location("flipper_emulator", MODULE_PATH)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        self.assertEqual(module.ROOT, ROOT)
        self.assertTrue(module.CAPABILITIES.is_file())

    def test_sanitized_oracle_snapshot(self):
        runner_path = MODULE_PATH.with_name("runner.py")
        spec = importlib.util.spec_from_file_location("flipper_runner", runner_path)
        runner = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(runner)
        result = runner.validate_oracle_snapshot(ROOT / ".ai" / "fz-emulator" / "snapshot")
        self.assertTrue(result["valid"], result["errors"])
        self.assertFalse(result["storage_contents"])
        self.assertEqual(result["radio_replay"]["classification"], "oracle-version-replay")
        self.assertFalse(result["radio_replay"]["cpu2_execution"])

    def test_sd_fixture_tree(self):
        runner_path = MODULE_PATH.with_name("runner.py")
        spec = importlib.util.spec_from_file_location("flipper_runner", runner_path)
        runner = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(runner)
        result = runner.validate_sd_tree(ROOT / ".ai" / "fz-emulator" / "sd-fixture")
        self.assertTrue(result["valid"], result["errors"][:3])
        self.assertGreater(result["files"], 900)


if __name__ == "__main__":
    unittest.main()
