"""Black-box and integration contract for Emulator v2's MCP server.

The suite deliberately uses temporary virtual storage and never enumerates or
opens physical USB/serial devices.  It tests observable MCP behaviour so the
server implementation can be refactored without rewriting the contract.
"""

from __future__ import annotations

import json
import hashlib
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PACKAGE = ROOT / "emulator_v2_mcp"
ENTRYPOINT = PACKAGE / "flipper_mcp_server.py"
REAL_ENGINE = ROOT / ".tools/flipper-fap-studio/runtime/stm32/source/target/release/stm32-emulator"
REAL_FIRMWARE = ROOT / "build/f7-firmware-C/firmware.bin"
REAL_SVD = ROOT / ".ai/logs/qemu-fw/fap-studio-profile/STM32WB55_CM4.svd"
ENGINE_SHA256 = "3e41b839305a63512a8a313a64f8e7978f77a6f5fa7355d911729c8403050b9c"
FIRMWARE_SHA256 = "ee6b41e921bf268926e3bb7b3c69e48cb6a9e078d788b3e74c288eefce5197f2"
sys.path.insert(0, str(PACKAGE))

# Pytest may import the repository-level ``tools`` namespace before collecting
# this module.  Use the package-qualified path so the auxiliary Emulator v2
# model cannot be shadowed by that unrelated namespace package.
from emulator_v2_mcp.tools.flipper_emulator.emulator import FlipperZeroEmulator  # noqa: E402
from integration_server import EmulatorV2MCPServer  # noqa: E402


def request(process: subprocess.Popen[str], payload: dict) -> dict:
    assert process.stdin is not None
    assert process.stdout is not None
    process.stdin.write(json.dumps(payload) + "\n")
    process.stdin.flush()
    line = process.stdout.readline()
    if not line:
        stderr = process.stderr.read() if process.stderr else ""
        raise AssertionError(f"MCP server closed stdout; stderr={stderr}")
    return json.loads(line)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class MCPStdioEndToEndTests(unittest.TestCase):
    def setUp(self) -> None:
        self.process = subprocess.Popen(
            [sys.executable, str(ENTRYPOINT)],
            cwd=PACKAGE,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
            env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
        )

    def tearDown(self) -> None:
        if self.process.poll() is None:
            self.process.terminate()
        try:
            self.process.communicate(timeout=3)
        except subprocess.TimeoutExpired:
            self.process.kill()
            self.process.communicate(timeout=3)

    def test_initialize_notification_list_and_representative_call(self) -> None:
        initialized = request(
            self.process,
            {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "initialize",
                "params": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {},
                    "clientInfo": {"name": "integration-test", "version": "1"},
                },
            },
        )
        self.assertEqual(initialized["jsonrpc"], "2.0")
        self.assertEqual(initialized["id"], 1)
        self.assertEqual(initialized["result"]["protocolVersion"], "2024-11-05")
        self.assertEqual(initialized["result"]["serverInfo"]["name"], "momentum-emulator-v2")

        # A notification has no response.  Sending the next request proves it
        # was consumed without corrupting or blocking the stdio stream.
        assert self.process.stdin is not None
        self.process.stdin.write(
            json.dumps({"jsonrpc": "2.0", "method": "notifications/initialized"}) + "\n"
        )
        self.process.stdin.flush()
        listed = request(self.process, {"jsonrpc": "2.0", "id": 2, "method": "tools/list"})
        tools = listed["result"]["tools"]
        self.assertEqual(len(tools), 15)
        self.assertEqual(len({tool["name"] for tool in tools}), 15)
        for tool in tools:
            self.assertIsInstance(tool["description"], str)
            self.assertTrue(tool["description"])
            self.assertEqual(tool["inputSchema"]["type"], "object")
            self.assertIsInstance(tool["inputSchema"].get("properties"), dict)

        called = request(
            self.process,
            {
                "jsonrpc": "2.0",
                "id": 3,
                "method": "tools/call",
                "params": {"name": "emulator_capabilities", "arguments": {}},
            },
        )
        self.assertFalse(called["result"].get("isError", False))
        capabilities = json.loads(called["result"]["content"][0]["text"])
        self.assertFalse(capabilities["mcp"]["hardware_access"])
        self.assertEqual(len(capabilities["mcp"]["tools"]), 15)

    def test_unknown_method_and_tool_have_standard_distinct_errors(self) -> None:
        method = request(self.process, {"jsonrpc": "2.0", "id": 10, "method": "not/a/method"})
        self.assertEqual(method["error"]["code"], -32601)
        tool = request(
            self.process,
            {
                "jsonrpc": "2.0",
                "id": 11,
                "method": "tools/call",
                "params": {"name": "not_a_tool", "arguments": {}},
            },
        )
        self.assertTrue(tool["result"]["isError"])
        self.assertIn("unknown tool", tool["result"]["content"][0]["text"].lower())


class MCPServerIntegrationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tempdir = tempfile.TemporaryDirectory()
        self.emulator = FlipperZeroEmulator(sd_card_path=self.tempdir.name)
        self.server = EmulatorV2MCPServer()
        self.server.emu.pty.stop()
        self.server.emu = self.emulator

    def tearDown(self) -> None:
        self.emulator.pty.stop()
        self.tempdir.cleanup()

    def call(self, name: str, arguments: dict, request_id: int = 1) -> dict:
        response = self.server.handle_request(
            {
                "jsonrpc": "2.0",
                "id": request_id,
                "method": "tools/call",
                "params": {"name": name, "arguments": arguments},
            }
        )
        assert response is not None
        return response

    def test_diagnostics_cover_every_declared_emulator_subsystem(self) -> None:
        response = self.call("emulator_capabilities", {})
        self.assertFalse(response["result"].get("isError", False))
        report = json.loads(response["result"]["content"][0]["text"])
        self.assertFalse(report["mcp"]["hardware_access"])
        self.assertEqual(set(report["mcp"]["backends"]), {"native-runner", "interactive-v2"})
        self.assertEqual(
            set(report["backends"]), {"native", "renode", "oracle"}
        )

    def test_sensible_long_run_is_deterministic_and_does_not_halt(self) -> None:
        # The Python model advances an arbitrary cycle quantum per step; one
        # 250M-cycle step is the meaningful equivalent of a 250M smoke run and
        # completes quickly enough for CI.
        initial_pc = self.emulator.core.pc
        self.emulator.step(250_000_000)
        state = self.emulator.core.dump_state()
        self.assertEqual(state["cycles"], 250_000_000)
        self.assertFalse(state["halted"])
        self.assertEqual(state["pc"], f"0x{initial_pc + 2:08X}")

    def test_storage_round_trip_stays_inside_temporary_virtual_card(self) -> None:
        target = Path(self.tempdir.name) / "integration" / "roundtrip.txt"
        target.parent.mkdir()
        target.write_text("emulator-only", encoding="utf-8")
        read = self.call("model_storage_read", {"path": "/ext/integration/roundtrip.txt"})
        result = json.loads(read["result"]["content"][0]["text"])
        self.assertEqual(result["utf8"], "emulator-only")
        self.assertEqual(target.read_text(encoding="utf-8"), "emulator-only")

    def test_path_traversal_is_rejected_without_touching_host_files(self) -> None:
        outside = Path(self.tempdir.name).parent / "mcp-host-sentinel.txt"
        outside.write_text("host-owned", encoding="utf-8")
        try:
            for name, arguments in (
                ("emulator_storage_read", {"path": "/ext/../../mcp-host-sentinel.txt"}),
                ("emulator_usb_rpc", {"operation": "storage_read", "path": "/ext/../../mcp-host-sentinel.txt"}),
            ):
                response = self.call(name, arguments)
                self.assertTrue(response["result"].get("isError"), name)
            self.assertEqual(outside.read_text(encoding="utf-8"), "host-owned")
        finally:
            outside.unlink(missing_ok=True)

    def test_invalid_arguments_are_reported_as_tool_errors(self) -> None:
        cases = (
            ("emulator_input", {"button": "INVALID"}),
            ("emulator_validate_artifact", {"path": str(Path(self.tempdir.name) / "missing")}),
            ("emulator_run_status", {"run_id": "missing"}),
            ("emulator_storage_read", {"path": "/ext/missing-content"}),
        )
        for name, arguments in cases:
            with self.subTest(name=name, arguments=arguments):
                response = self.call(name, arguments)
                self.assertTrue(response["result"].get("isError"))

    def test_spec_validation_covers_the_published_schema_and_all_artifacts(self) -> None:
        root = Path(self.tempdir.name)
        firmware = root / "firmware.bin"
        firmware.write_bytes(b"fw")
        cases = (
            {
                "firmware": str(firmware),
                "output": str(root / "out"),
                "oracle_snapshot": str(root / "missing-oracle"),
            },
            {
                "firmware": str(firmware),
                "output": str(root / "out"),
                "sd_tree": str(root / "missing-sd-tree"),
            },
            {"firmware": str(firmware), "output": str(root / "out"), "max_instructions": 0},
            {"firmware": str(firmware), "output": str(root / "out"), "unexpected": True},
        )
        for index, value in enumerate(cases):
            spec = root / f"invalid-{index}.json"
            spec.write_text(json.dumps(value), encoding="utf-8")
            with self.subTest(spec=value):
                response = self.call("emulator_validate_spec", {"spec_path": str(spec)})
                self.assertFalse(
                    json.loads(response["result"]["content"][0]["text"])["valid"]
                )

    def test_snapshot_metadata_uses_the_canonical_oracle_validator(self) -> None:
        snapshot = ROOT / ".ai/fz-emulator/snapshot"
        completed = subprocess.run(
            [
                sys.executable,
                "-c",
                (
                    "import json; from pathlib import Path; "
                    "from tools.flipper_emulator.runner import validate_oracle_snapshot; "
                    f"print(json.dumps(validate_oracle_snapshot(Path({str(snapshot)!r}))))"
                ),
            ],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=True,
        )
        canonical = json.loads(completed.stdout)
        result = json.loads(
            self.call("emulator_snapshot_metadata", {"path": str(snapshot)})["result"]["content"][0]["text"]
        )
        self.assertEqual(result, canonical)

    def test_tool_arguments_are_enforced_against_advertised_schema(self) -> None:
        # additionalProperties=false and required/type constraints are part of
        # the advertised MCP contract, not optional documentation.
        extra = self.call("emulator_capabilities", {"unexpected": True})
        self.assertTrue(extra["result"].get("isError"))
        wrong_type = self.call("emulator_events", {"run_id": 7, "offset": "zero"})
        self.assertTrue(wrong_type["result"].get("isError"))

    def test_resources_are_readable(self) -> None:
        resources = self.server.handle_request(
            {"jsonrpc": "2.0", "id": 20, "method": "resources/list"}
        )
        assert resources is not None
        for resource in resources["result"]["resources"]:
            response = self.server.handle_request(
                {
                    "jsonrpc": "2.0",
                    "id": 21,
                    "method": "resources/read",
                    "params": {"uri": resource["uri"]},
                }
            )
            assert response is not None
            self.assertTrue(response["result"]["contents"][0]["text"])

    def test_native_background_run_honors_250m_instruction_spec(self) -> None:
        root = Path(self.tempdir.name)
        firmware = root / "firmware.bin"
        firmware.write_bytes(b"\x00" * 32)
        svd = root / "chip.svd"
        svd.write_text("<device/>", encoding="utf-8")
        engine = root / "fake-engine"
        engine.write_text(
            "#!/bin/sh\nprintf '[clk=250000000 pc=0x08000102] FLIPPER_FRAME 00\\n'\n",
            encoding="utf-8",
        )
        engine.chmod(0o755)
        output = root / "output"
        spec = root / "spec.json"
        spec.write_text(
            json.dumps(
                {
                    "firmware": str(firmware),
                    "engine": str(engine),
                    "svd": str(svd),
                    "output": str(output),
                    "max_instructions": 250_000_000,
                }
            ),
            encoding="utf-8",
        )
        started = self.call("emulator_run", {"spec_path": str(spec)})
        start_state = json.loads(started["result"]["content"][0]["text"])
        run_id = start_state["run_id"]
        import time

        for _ in range(100):
            status = json.loads(
                self.call("emulator_run_status", {"run_id": run_id})["result"]["content"][0]["text"]
            )
            if status["phase"] in {"succeeded", "failed"}:
                break
            time.sleep(0.02)
        self.assertEqual(status["phase"], "succeeded", status)
        report = json.loads(
            self.call("emulator_report", {"run_id": run_id})["result"]["content"][0]["text"]
        )
        self.assertEqual(report["returncode"], 0)
        self.assertIn("250000000", report["command"])
        events = json.loads(
            self.call("emulator_events", {"run_id": run_id, "offset": 0, "limit": 10})["result"]["content"][0]["text"]
        )
        self.assertEqual(events["events"][0]["instruction"], 250_000_000)

    def test_real_compiled_engine_runs_current_firmware_for_250m(self) -> None:
        """Acceptance gate: canonical engine + firmware, never a fake backend."""
        for artifact in (REAL_ENGINE, REAL_FIRMWARE, REAL_SVD):
            self.assertTrue(artifact.is_file(), artifact)
        self.assertEqual(sha256(REAL_ENGINE), ENGINE_SHA256)
        self.assertEqual(sha256(REAL_FIRMWARE), FIRMWARE_SHA256)

        root = Path(self.tempdir.name)
        output = root / "real-output"
        spec = root / "real-spec.json"
        spec.write_text(
            json.dumps(
                {
                    "firmware": str(REAL_FIRMWARE),
                    "engine": str(REAL_ENGINE),
                    "svd": str(REAL_SVD),
                    "output": str(output),
                    "max_instructions": 250_000_000,
                    "live_control": True,
                }
            ),
            encoding="utf-8",
        )
        started = json.loads(
            self.call("emulator_run", {"spec_path": str(spec)})["result"]["content"][0]["text"]
        )
        import time

        input_sent = False
        for _ in range(120):
            status = json.loads(
                self.call("emulator_run_status", {"run_id": started["run_id"]})["result"]["content"][0]["text"]
            )
            if (
                not input_sent
                and status["phase"] == "running"
                and status.get("native_runtime", {}).get("control_fifo")
            ):
                accepted = self.call(
                    "emulator_input",
                    {"run_id": started["run_id"], "button": "OK", "action": "PRESS"},
                )
                self.assertFalse(accepted["result"].get("isError", False), accepted)
                input_sent = True
            if status["phase"] in {"succeeded", "failed"}:
                break
            time.sleep(0.25)
        self.assertTrue(input_sent, status)
        self.assertEqual(status["phase"], "succeeded", status)
        report = json.loads(
            self.call("emulator_report", {"run_id": started["run_id"]})["result"]["content"][0]["text"]
        )
        self.assertEqual(report["returncode"], 0)
        self.assertEqual(report["engine"]["sha256"], ENGINE_SHA256)
        self.assertEqual(report["firmware"]["sha256"], FIRMWARE_SHA256)
        self.assertEqual(report["command"][report["command"].index("--max-instructions") + 1], "250000000")
        self.assertTrue(report["differential"]["stable_ui_observed"])
        events = json.loads(
            self.call("emulator_events", {"run_id": started["run_id"], "limit": 1000})["result"]["content"][0]["text"]
        )
        kinds = {event["kind"] for event in events["events"]}
        self.assertTrue({"frame", "input"}.issubset(kinds))
        native_screen = self.call(
            "emulator_screen", {"run_id": started["run_id"], "format": "raw_hex"}
        )
        self.assertFalse(native_screen["result"].get("isError", False))
        self.assertEqual(len(native_screen["result"]["content"][0]["text"]), 2048)

    def test_screen_and_input_are_bound_to_a_native_run(self) -> None:
        """Native control must not silently act on the duplicate Python model."""
        schemas = {tool["name"]: tool["inputSchema"] for tool in self.server.tools}
        for tool_name in ("emulator_screen", "emulator_input"):
            schema = schemas[tool_name]
            self.assertIn("run_id", schema["properties"], tool_name)
            self.assertIn("run_id", schema.get("required", []), tool_name)
        missing_run = self.call("emulator_screen", {})
        self.assertTrue(missing_run["result"].get("isError"))


class DocumentationAccuracyTests(unittest.TestCase):
    def test_readme_does_not_claim_private_identity_or_physical_rf(self) -> None:
        readme = (PACKAGE / "README.md").read_text(encoding="utf-8").lower()
        self.assertNotIn("asch1rp", readme)
        self.assertNotIn("transmisión de claves", readme)
        self.assertIn("no abre hardware", readme)
        self.assertIn("replay", readme)


if __name__ == "__main__":
    unittest.main()
