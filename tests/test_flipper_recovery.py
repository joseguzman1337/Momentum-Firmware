import importlib.util
import struct
import tempfile
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("flipper_recovery", ROOT / "scripts/flipper_recovery.py")
r = importlib.util.module_from_spec(SPEC); SPEC.loader.exec_module(r)
REGISTER_SPEC = importlib.util.spec_from_file_location("flipper_recovery_register", ROOT / ".ai/mcp/servers/flipper_recovery/register.py")
registration = importlib.util.module_from_spec(REGISTER_SPEC); REGISTER_SPEC.loader.exec_module(registration)

def elf32(path: Path, address: int, size: int) -> Path:
    return elf32_segments(path, [(address, size)])

def elf32_segments(path: Path, segments: list[tuple[int, int]]) -> Path:
    header = struct.pack("<16sHHIIIIIHHHHHH", b"\x7fELF\x01\x01\x01" + b"\0" * 9, 2, 40, 1, 0, 52, 0, 0, 52, 32, len(segments), 0, 0, 0)
    offset = 52 + 32 * len(segments); programs = []; payload = b""
    for address, size in segments:
        programs.append(struct.pack("<IIIIIIII", 1, offset + len(payload), address, address, size, size, 5, 4)); payload += b"X" * size
    path.write_bytes(header + b"".join(programs) + payload)
    return path

class RecoveryTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(); self.root = Path(self.temp.name)
    def tearDown(self): self.temp.cleanup()
    def test_boundary_equal_is_accepted(self):
        image = elf32(self.root / "safe.elf", r.CPU2_BOUNDARY - 16, 16)
        self.assertEqual(r.validate_image(image)["headroom"], 0)
    def test_boundary_crossing_is_refused(self):
        image = elf32(self.root / "unsafe.elf", r.CPU2_BOUNDARY - 16, 17)
        with self.assertRaisesRegex(ValueError, "CPU2 boundary"): r.validate_image(image)
    def test_safe_plus_segment_at_boundary_is_refused(self):
        image = elf32_segments(self.root / "mixed.elf", [(r.FLASH_BASE, 16), (r.CPU2_BOUNDARY, 16)])
        with self.assertRaisesRegex(ValueError, "starts at/beyond"): r.validate_image(image)
    def test_boundary_only_segment_is_refused(self):
        image = elf32(self.root / "boundary.elf", r.CPU2_BOUNDARY, 16)
        with self.assertRaisesRegex(ValueError, "starts at/beyond"): r.validate_image(image)
    def test_flash_requires_confirmation(self):
        image = elf32(self.root / "safe.elf", r.FLASH_BASE, 16)
        with self.assertRaisesRegex(PermissionError, "refusing flash"): r.flash_usb(image, root=self.root, confirm="")
    def test_status_is_read_only(self):
        with mock.patch.object(r, "_pid_alive", return_value=False): r.monitor_status(self.root)
        self.assertFalse((self.root / ".recovery").exists())
    def test_readonly_observation_while_armed_cannot_flash_or_write(self):
        recovery = self.root / ".recovery"; recovery.mkdir(); arm = recovery / "armed.json"; arm.write_text('{"image":"armed"}\n')
        before = arm.read_bytes()
        with mock.patch.object(r, "devices", return_value={}), mock.patch.object(r, "flash_swd") as flash:
            r.monitor_observation(self.root)
        self.assertEqual(arm.read_bytes(), before); flash.assert_not_called()
    def test_singleton_claim_prevents_spawn(self):
        recovery = self.root / ".recovery"; recovery.mkdir(); (recovery / "monitor.pid").write_text("")
        with mock.patch.object(r, "monitor_status", return_value={"running": False, "external_watchers": []}), mock.patch.object(r.subprocess, "Popen") as spawn:
            result = r.monitor_start(self.root)
        self.assertEqual(result["reason"], "singleton_claimed"); spawn.assert_not_called()
    def test_history_records_transition_not_identical_cycle(self):
        probe = {"device": "/dev/test", "kind": "blackmagic_devboard"}
        inventory = {"source": "test", "devices": [probe], "blackmagic": [probe], "flipper": []}
        with mock.patch.object(r, "devices", return_value=inventory):
            r.monitor_once(self.root, heartbeat_seconds=9999); r.monitor_once(self.root, heartbeat_seconds=9999)
        history = r.get_monitor_history(self.root)
        self.assertEqual(len(history), 1); self.assertEqual(history[0]["event"], "transition"); self.assertEqual(history[0]["state"], "devboard_online")
    def test_evidence_redaction_and_truncation(self):
        value = r.sanitized_evidence("token=supersecret " + "x" * 100, limit=30)
        self.assertNotIn("supersecret", value); self.assertTrue(value.endswith("...[truncated]"))
    def test_backoff_is_bounded(self):
        self.assertEqual(r.monitor_backoff(0), 1.0); self.assertEqual(r.monitor_backoff(3), 8.0); self.assertEqual(r.monitor_backoff(99), 30.0)
    def test_history_append_persists_across_restart(self):
        path = r.monitor_paths(self.root, create=True)["history"]
        r.append_history(path, {"timestamp": 1, "state": "one"}); r.append_history(path, {"timestamp": 2, "state": "two"})
        self.assertEqual([x["state"] for x in r.get_monitor_history(self.root)], ["one", "two"])
    def test_stale_pid_is_never_signaled(self):
        recovery = self.root / ".recovery"; recovery.mkdir(); (recovery / "monitor.pid").write_text("123\n")
        stale = {"running": False, "pid": None, "external_watchers": [], "state": None, "armed": None, "log": "x"}
        with mock.patch.object(r, "monitor_status", return_value=stale), mock.patch.object(r.os, "kill") as kill:
            result = r.monitor_stop(self.root)
        self.assertFalse(result["signaled"]); kill.assert_not_called()
    def test_ioreg_fallback_identifies_blackmagic_gdb_and_uart(self):
        output = '+-o Blackmagic ESP32  <class IOUSBHostDevice>\n  {\n    "idVendor" = 12346\n    "idProduct" = 16385\n    "USB Product Name" = "Blackmagic ESP32"\n  }\n'
        completed = type("Result", (), {"stdout": output, "returncode": 0})()
        with mock.patch.dict("sys.modules", {"serial": None}), mock.patch.object(r.subprocess, "run", return_value=completed), mock.patch.object(r.glob, "glob", return_value=["/dev/cu.usbmodem1103", "/dev/cu.usbmodem1101"]):
            inventory = r.devices()
        self.assertEqual(inventory["source"], "ioreg_glob_fallback")
        self.assertEqual(inventory["blackmagic"][0]["device"], "/dev/cu.usbmodem1101")
        self.assertEqual(next(d for d in inventory["devices"] if d["device"].endswith("1103"))["kind"], "blackmagic_uart")
    def test_external_watcher_matches_executable_not_shell_text(self):
        ps = "88018 1 /usr/local/bin/qFlipper-cli qFlipper-cli --debug-level 2\n90000 1 /bin/zsh zsh -c echo qflipper-cli auto_flash_devboard\n"
        completed = type("Result", (), {"stdout": ps, "returncode": 0})()
        with mock.patch.object(r.subprocess, "run", return_value=completed), mock.patch.object(r.os, "getpid", return_value=42):
            watchers = r._external_watchers()
        self.assertEqual(len(watchers), 1); self.assertTrue(watchers[0].startswith("88018 "))
    def test_registration_targets_top_level_not_nested_mcpservers(self):
        original = '{"projects":{"/Users/x":{"mcpServers":{}}},"mcpServers":{"existing":{"command":"keep"}}}\n'
        updated = registration.desired(Path("/Users/x/.claude.json"), original)
        parsed = __import__("json").loads(updated)
        self.assertEqual(parsed["projects"]["/Users/x"]["mcpServers"], {})
        self.assertEqual(parsed["mcpServers"]["existing"]["command"], "keep")
        self.assertIn(registration.NAME, parsed["mcpServers"])
    def test_registration_creates_top_level_when_only_nested_exists(self):
        original = '{"projects":{"/Users/x":{"mcpServers":{}}}}\n'
        parsed = __import__("json").loads(registration.desired(Path("/Users/x/.claude.json"), original))
        self.assertEqual(parsed["projects"]["/Users/x"]["mcpServers"], {})
        self.assertEqual(parsed["mcpServers"][registration.NAME]["command"], registration.PYTHON)
    @unittest.skipUnless(registration.yaml is not None, "PyYAML is provided by the Sensei venv")
    def test_hermes_registration_is_inside_top_level_mcp_servers(self):
        original = "# keep semantics\nmodel:\n  default: glm\nmcp_servers:\n  existing:\n    command: keep\nruntime:\n  timeout: 180\n"
        updated = registration.desired(Path("/Users/x/.hermes/config.yaml"), original)
        parsed = registration.yaml.safe_load(updated)
        self.assertEqual(parsed["model"]["default"], "glm")
        self.assertEqual(parsed["runtime"]["timeout"], 180)
        self.assertEqual(parsed["mcp_servers"]["existing"]["command"], "keep")
        self.assertEqual(parsed["mcp_servers"][registration.NAME]["command"], registration.PYTHON)
    def test_good_state_false_for_devboard_only(self):
        inventory = {"source": "test", "devices": [], "blackmagic": [{"vid": 0x303A, "pid": 0x4001}], "flipper": []}
        with mock.patch.object(r, "devices", return_value=inventory): result = r.verify_good_state()
        self.assertFalse(result["good_state"])
    def test_good_state_true_for_real_flipper_cdc(self):
        cdc = {"device": "/dev/cu.usbmodemflip_test", "vid": 0x0483, "pid": 0x5740, "description": "Flipper Zero"}
        inventory = {"source": "test", "devices": [cdc], "blackmagic": [], "flipper": [cdc]}
        with mock.patch.object(r, "devices", return_value=inventory): result = r.verify_good_state()
        self.assertTrue(result["good_state"]); self.assertIn("usbmodemflip_test", result["evidence"][0])
    def test_recovery_does_not_duplicate_matching_successful_hash(self):
        image = elf32(self.root / "safe.elf", r.FLASH_BASE, 16); digest = r.image_sha256(image)
        prior = {"timestamp": 1, "state": "flash_succeeded", "image_sha256": digest}
        bad = {"good_state": False}
        status = {"armed": None}
        with mock.patch.object(r, "verify_good_state", return_value=bad), mock.patch.object(r, "monitor_status", return_value=status), mock.patch.object(r, "get_monitor_history", return_value=[prior]), mock.patch.object(r, "monitor_once") as cycle:
            result = r.recover_to_good_state(image, root=self.root, port="/dev/test", confirm=r.CONFIRM, build_first=False)
        self.assertEqual(result["action"], "awaiting_good_state"); self.assertTrue(result["duplicate_flash_prevented"]); cycle.assert_not_called()
    def test_recovery_remains_incomplete_until_postverify(self):
        image = elf32(self.root / "safe.elf", r.FLASH_BASE, 16); bad = {"good_state": False}
        status = {"armed": None}
        cycle_result = {"state": "flash_succeeded", "action": "swd_flash"}
        with mock.patch.object(r, "verify_good_state", side_effect=[bad, bad]), mock.patch.object(r, "monitor_status", return_value=status), mock.patch.object(r, "get_monitor_history", return_value=[]), mock.patch.object(r, "monitor_once", return_value=cycle_result), mock.patch.object(r, "monitor_start", return_value={"started": True}):
            result = r.recover_to_good_state(image, root=self.root, port="/dev/test", confirm=r.CONFIRM, build_first=False)
        self.assertFalse(result["complete"]); self.assertEqual(result["action"], "awaiting_good_state")
    def test_absence_flapping_preserves_effective_state(self):
        probe = {"device": "/dev/test", "kind": "blackmagic_devboard"}
        present = {"source": "ioreg", "devices": [probe], "blackmagic": [probe], "flipper": []}
        absent = {"source": "ioreg_transient", "devices": [], "blackmagic": [], "flipper": []}
        with mock.patch.object(r, "devices", side_effect=[present, absent, present, absent]):
            states = [r.monitor_once(self.root)["state"] for _ in range(4)]
        self.assertEqual(states, ["devboard_online"] * 4)
        self.assertEqual(r._read_json(r.monitor_paths(self.root)["state"])["miss_count"], 1)
    def test_sustained_absence_transitions_only_at_threshold(self):
        absent = {"source": "ioreg", "devices": [], "blackmagic": [], "flipper": []}
        with mock.patch.object(r, "devices", return_value=absent):
            results = [r.monitor_once(self.root) for _ in range(3)]
        self.assertEqual([x["state"] for x in results], ["unknown", "unknown", "absent"])
        self.assertEqual([x["miss_count"] for x in results], [1, 2, 3])
    def test_recovery_resets_miss_count(self):
        probe = {"device": "/dev/test", "kind": "blackmagic_devboard"}
        present = {"source": "ioreg", "devices": [probe], "blackmagic": [probe], "flipper": []}
        absent = {"source": "ioreg", "devices": [], "blackmagic": [], "flipper": []}
        with mock.patch.object(r, "devices", side_effect=[present, absent, absent, present]):
            results = [r.monitor_once(self.root) for _ in range(4)]
        self.assertEqual(results[-1]["state"], "devboard_online"); self.assertEqual(results[-1]["miss_count"], 0)
    def test_miss_state_and_journal_persist_across_restart(self):
        probe = {"device": "/dev/test", "kind": "blackmagic_devboard"}
        present = {"source": "ioreg", "devices": [probe], "blackmagic": [probe], "flipper": []}
        absent = {"source": "ioreg_miss", "devices": [], "blackmagic": [], "flipper": []}
        with mock.patch.object(r, "devices", side_effect=[present, absent]): r.monitor_once(self.root); r.monitor_once(self.root)
        before = r.get_monitor_history(self.root)
        with mock.patch.object(r, "devices", return_value=absent): after_restart = r.monitor_once(self.root)
        after = r.get_monitor_history(self.root)
        self.assertEqual(after_restart["miss_count"], 2); self.assertEqual(after_restart["state"], "devboard_online")
        self.assertEqual(after[:len(before)], before); self.assertEqual(after[-1]["event"], "transient_miss")
    def test_pre_hysteresis_state_migrates_devices_on_transient_miss(self):
        probe = {"device": "/dev/cu.usbmodem1101", "kind": "blackmagic_devboard"}
        legacy_inventory = {"source": "ioreg", "devices": [probe], "blackmagic": [probe], "flipper": []}
        state_path = r.monitor_paths(self.root, create=True)["state"]
        r.atomic_json(state_path, {"state": "devboard_online", "devices": legacy_inventory, "cycle": 7})
        absent = {"source": "ioreg_miss", "devices": [], "blackmagic": [], "flipper": []}
        with mock.patch.object(r, "devices", return_value=absent): result = r.monitor_once(self.root)
        self.assertEqual(result["state"], "devboard_online")
        self.assertEqual(result["devices"], legacy_inventory)
        self.assertEqual(result["last_known_devices"], legacy_inventory)
        self.assertEqual(result["miss_count"], 1)
    def _armed_swd_fixture(self):
        image = elf32(self.root / "safe.elf", r.FLASH_BASE, 16)
        r.arm_monitor(image, root=self.root, port="/dev/test", confirm=r.CONFIRM)
        probe = {"device": "/dev/test", "kind": "blackmagic_devboard"}
        inventory = {"source": "test", "devices": [probe], "blackmagic": [probe], "flipper": []}
        return image, inventory
    def test_swd_rc1_retains_arm_and_increments_attempts(self):
        _image, inventory = self._armed_swd_fixture()
        failed = type("Result", (), {"returncode": 1, "stdout": "", "stderr": "load failed"})()
        with mock.patch.object(r, "devices", return_value=inventory): result = r.monitor_once(self.root, runner=lambda *a, **k: failed)
        arm = r._read_json(r.monitor_paths(self.root)["arm"])
        self.assertEqual(result["state"], "flash_failed"); self.assertEqual(arm["attempts"], 1); self.assertGreater(arm["next_retry_at"], arm["last_attempt_at"])
    def test_swd_rc0_without_load_evidence_retains_arm(self):
        _image, inventory = self._armed_swd_fixture()
        ambiguous = type("Result", (), {"returncode": 0, "stdout": "connected", "stderr": ""})()
        with mock.patch.object(r, "devices", return_value=inventory): r.monitor_once(self.root, runner=lambda *a, **k: ambiguous)
        self.assertEqual(r._read_json(r.monitor_paths(self.root)["arm"])["attempts"], 1)
    def test_verified_successful_load_clears_arm(self):
        _image, inventory = self._armed_swd_fixture()
        success = type("Result", (), {"returncode": 0, "stdout": "Loading section .text\nTransfer rate: 20 KB/s", "stderr": ""})()
        with mock.patch.object(r, "devices", return_value=inventory): result = r.monitor_once(self.root, runner=lambda *a, **k: success)
        self.assertEqual(result["state"], "flash_succeeded"); self.assertTrue(result["verified_load"]); self.assertFalse(r.monitor_paths(self.root)["arm"].exists())
    def test_next_retry_prevents_runner_call(self):
        _image, inventory = self._armed_swd_fixture(); arm_path = r.monitor_paths(self.root)["arm"]
        arm = r._read_json(arm_path); arm["next_retry_at"] = __import__("time").time() + 600; r.atomic_json(arm_path, arm)
        runner = mock.Mock(side_effect=AssertionError("must not run"))
        with mock.patch.object(r, "devices", return_value=inventory): result = r.monitor_once(self.root, runner=runner)
        self.assertEqual(result["action"], "retry_wait"); runner.assert_not_called()
    def test_retry_metadata_survives_restart_cycle(self):
        _image, inventory = self._armed_swd_fixture()
        failed = type("Result", (), {"returncode": 1, "stdout": "", "stderr": "error while loading"})()
        with mock.patch.object(r, "devices", return_value=inventory): r.monitor_once(self.root, runner=lambda *a, **k: failed)
        persisted = r._read_json(r.monitor_paths(self.root)["arm"])
        runner = mock.Mock(side_effect=AssertionError("backoff must survive restart"))
        with mock.patch.object(r, "devices", return_value=inventory): result = r.monitor_once(self.root, runner=runner)
        self.assertEqual(result["action"], "retry_wait"); self.assertEqual(r._read_json(r.monitor_paths(self.root)["arm"])["attempts"], persisted["attempts"]); runner.assert_not_called()
    def test_dry_run_constructs_swd_argv_without_execution(self):
        image = elf32(self.root / "safe.elf", r.FLASH_BASE, 16)
        result = r.flash_swd(image, root=self.root, port="/dev/test-gdb", confirm=r.CONFIRM, dry_run=True)
        self.assertTrue(result["command"][0].endswith("arm-none-eabi-gdb")); self.assertIn("target extended-remote /dev/test-gdb", result["command"])
    @mock.patch.object(r, "devices", return_value={"source": "test", "devices": [], "blackmagic": [], "flipper": []})
    @mock.patch.object(r, "flash_swd", side_effect=AssertionError("must not flash"))
    def test_monitor_observes_without_arm(self, flash, _devices):
        self.assertEqual(r.monitor_once(self.root)["action"], "observe_only"); flash.assert_not_called()
    def test_armed_monitor_hash_mismatch_refuses(self):
        image = elf32(self.root / "safe.elf", r.FLASH_BASE, 16)
        r.arm_monitor(image, root=self.root, port="/dev/test", confirm=r.CONFIRM); image.write_bytes(image.read_bytes() + b"changed")
        inventory = {"source": "test", "devices": [{}], "blackmagic": [{}], "flipper": []}
        with mock.patch.object(r, "devices", return_value=inventory), mock.patch.object(r, "flash_swd") as flash: result = r.monitor_once(self.root)
        self.assertEqual(result["action"], "refused"); self.assertIn("hash changed", result["error"]); flash.assert_not_called()
    def test_build_command_is_injected(self):
        captured = {}
        def fake(argv, **kwargs):
            captured["argv"] = argv; return type("Result", (), {"returncode": 1, "stdout": "", "stderr": "expected"})()
        result = r.build(root=self.root, runner=fake)
        self.assertEqual(captured["argv"], [str(self.root / "fbt"), "build/f7-firmware-C/firmware.elf", "SKIP_EXTERNAL=1"]); self.assertFalse(result["ok"])

if __name__ == "__main__": unittest.main()
