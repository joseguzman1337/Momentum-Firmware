import json
import stat
import tempfile
import unittest
from pathlib import Path

from tools.flipper_emulator.runner import load_spec, parse_trace, profile, run


class RunnerTests(unittest.TestCase):
    def test_profile_has_flipper_devices(self):
        text = profile("full.bin", "sd-card.img")
        for value in ("STM32WB55_CM4.svd", "SPI2", "PC10", "PC11", "PC12", "ST7567"):
            self.assertIn(value.lower() if value == "ST7567" else value, text.lower() if value == "ST7567" else text)

    def test_trace_is_stable_and_structured(self):
        events = parse_trace("[clk=00000042 pc=0x08001234] INFO  FLIPPER_INPUT ok PRESS\n")
        self.assertEqual(events, [{"sequence": 0, "instruction": 42, "pc": "0x08001234", "kind": "input", "payload": "ok PRESS"}])

    def test_invalid_input_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "spec.json"
            path.write_text(json.dumps({"firmware": "x", "output": "y", "inputs": [{"button": "ok", "action": "DOWN"}]}))
            with self.assertRaises(ValueError):
                load_spec(path)

    def test_headless_process_isolation_and_artifacts(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            firmware = root / "fw.bin"; firmware.write_bytes(b"firmware")
            svd = root / "chip.svd"; svd.write_text("svd")
            engine = root / "engine"
            engine.write_text("#!/bin/sh\nprintf '[clk=00000007 pc=0x08000001] INFO  FLIPPER_FRAME abcd\\n'\n")
            engine.chmod(engine.stat().st_mode | stat.S_IXUSR)
            output = root / "out"
            spec = root / "spec.json"
            spec.write_text(json.dumps({"firmware": str(firmware), "svd": str(svd), "engine": str(engine), "output": str(output), "max_instructions": 1}))
            self.assertEqual(run(spec), 0)
            report = json.loads((output / "report.json").read_text())
            self.assertEqual(report["event_count"], 1)
            self.assertEqual((output / "stage/full.bin").read_bytes(), b"firmware")
            self.assertTrue((output / "events.jsonl").is_file())


if __name__ == "__main__":
    unittest.main()
