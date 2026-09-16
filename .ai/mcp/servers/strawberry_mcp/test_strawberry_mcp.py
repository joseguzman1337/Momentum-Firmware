"""Unit tests for Strawberry MCP safety boundaries; no device access."""
from __future__ import annotations

import asyncio
import os
import sys
import tempfile
import time
import types
import unittest
from pathlib import Path
from unittest.mock import AsyncMock, patch

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import furi_utils  # noqa: E402

try:
    import main  # noqa: E402
except ModuleNotFoundError as error:
    if error.name != "mcp":
        raise
    class _FakeFastMCP:
        def __init__(self, _name: str) -> None:
            pass
        def tool(self):
            return lambda function: function
        def run(self) -> None:
            raise AssertionError("tests must not start the MCP server")
    mcp_module = types.ModuleType("mcp")
    server_module = types.ModuleType("mcp.server")
    fastmcp_module = types.ModuleType("mcp.server.fastmcp")
    fastmcp_module.FastMCP = _FakeFastMCP
    sys.modules.update({"mcp": mcp_module, "mcp.server": server_module, "mcp.server.fastmcp": fastmcp_module})
    import main  # noqa: E402


class ProcessHelperTests(unittest.IsolatedAsyncioTestCase):
    async def test_argv_is_not_interpreted_by_shell(self) -> None:
        code, stdout, stderr = await furi_utils.run_command_async(
            [sys.executable, "-c", "import sys; print(sys.argv[1])", "$(echo injected)"],
            timeout=5,
        )
        self.assertEqual(code, 0)
        self.assertEqual(stdout.strip(), "$(echo injected)")
        self.assertEqual(stderr, "")

    async def test_timeout_has_structured_return_code(self) -> None:
        code, _, stderr = await furi_utils.run_command_async(
            [sys.executable, "-c", "import time; time.sleep(5)"], timeout=0.01
        )
        self.assertEqual(code, 124)
        self.assertIn("timed out", stderr)

    async def test_nonstream_capture_is_bounded_while_draining_large_output(self) -> None:
        with patch.object(furi_utils, "MAX_CAPTURE_BYTES", 64):
            code, stdout, stderr = await furi_utils.run_command_async(
                [sys.executable, "-c", "import sys; sys.stdout.write('A'*5000+'TAIL'); sys.stderr.write('B'*5000+'END')"],
                timeout=5,
            )
        self.assertEqual(code, 0)
        self.assertIn("truncated", stdout)
        self.assertIn("truncated", stderr)
        self.assertTrue(stdout.endswith("TAIL"))
        self.assertTrue(stderr.endswith("END"))

    async def test_streaming_truncates_old_log_and_captures_both_streams(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            log = Path(directory) / "run.log"
            log.write_text("stale", encoding="utf-8")
            code, stdout, stderr = await furi_utils.run_command_async_stream(
                [sys.executable, "-c", "import sys; print('out'); print('err', file=sys.stderr)"],
                log,
                timeout=5,
            )
            self.assertEqual((code, stdout.strip(), stderr.strip()), (0, "out", "err"))
            logged = log.read_text(encoding="utf-8")
            self.assertNotIn("stale", logged)
            self.assertIn("[stdout] out", logged)
            self.assertIn("[stderr] err", logged)

    async def test_stream_timeout_also_covers_process_wait_after_pipes_close(self) -> None:
        """A child that closes both pipes must not bypass the overall deadline."""
        if os.name == "nt":
            self.skipTest("file-descriptor close command is POSIX-specific")
        with tempfile.TemporaryDirectory() as directory:
            started = time.monotonic()
            code, _, stderr = await furi_utils.run_command_async_stream(
                [
                    sys.executable,
                    "-c",
                    "import os,time; os.close(1); os.close(2); time.sleep(5)",
                ],
                Path(directory) / "closed-pipes.log",
                timeout=0.05,
            )
            elapsed = time.monotonic() - started
        self.assertEqual(code, 124)
        self.assertIn("timed out", stderr)
        self.assertLess(elapsed, 2.0)

    async def test_stream_timeout_kills_process_that_ignores_terminate(self) -> None:
        if os.name == "nt":
            self.skipTest("SIGTERM behavior is POSIX-specific")
        with tempfile.TemporaryDirectory() as directory:
            with patch.object(furi_utils, "PROCESS_STOP_TIMEOUT", 0.05):
                started = time.monotonic()
                code, _, stderr = await furi_utils.run_command_async_stream(
                    [
                        sys.executable,
                        "-c",
                        "import signal,time; signal.signal(signal.SIGTERM, signal.SIG_IGN); print('ready', flush=True); time.sleep(5)",
                    ],
                    Path(directory) / "kill.log",
                    timeout=0.1,
                )
                elapsed = time.monotonic() - started
        self.assertEqual(code, 124)
        self.assertIn("timed out", stderr)
        self.assertLess(elapsed, 2.0)

    async def test_stream_reader_failure_stops_and_reaps_process(self) -> None:
        class FailingStream:
            async def read(self, _size: int) -> bytes:
                raise RuntimeError("reader failed")

        class EmptyStream:
            async def read(self, _size: int) -> bytes:
                return b""

        class FakeProcess:
            def __init__(self) -> None:
                self.stdout = FailingStream()
                self.stderr = EmptyStream()
                self.returncode = None
                self.terminated = False
                self.reaped = False
                self._done = asyncio.Event()

            def terminate(self) -> None:
                self.terminated = True
                self.returncode = -15
                self._done.set()

            def kill(self) -> None:
                self.returncode = -9
                self._done.set()

            async def wait(self) -> int:
                await self._done.wait()
                self.reaped = True
                return self.returncode or 0

        process = FakeProcess()
        with tempfile.TemporaryDirectory() as directory:
            with patch.object(
                furi_utils.asyncio,
                "create_subprocess_exec",
                new=AsyncMock(return_value=process),
            ):
                code, stdout, stderr = await furi_utils.run_command_async_stream(
                    ["offline-fake"], Path(directory) / "reader-error.log", timeout=1
                )
        self.assertEqual(code, 127)
        self.assertEqual(stdout, "")
        self.assertIn("reader failed", stderr)
        self.assertTrue(process.terminated)
        self.assertTrue(process.reaped)

    async def test_stream_capture_and_live_log_are_bounded(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            log = Path(directory) / "bounded.log"
            with (
                patch.object(furi_utils, "MAX_CAPTURE_BYTES", 64),
                patch.object(furi_utils, "MAX_LOG_BYTES", 128),
            ):
                code, stdout, stderr = await furi_utils.run_command_async_stream(
                    [
                        sys.executable,
                        "-c",
                        "import sys; sys.stdout.write('A'*512+'TAIL'); sys.stderr.write('B'*512+'ERRTAIL')",
                    ],
                    log,
                    timeout=5,
                )
            log_size = log.stat().st_size
            log_bytes = log.read_bytes()
        self.assertEqual(code, 0)
        self.assertIn("truncated", stdout)
        self.assertTrue(stdout.endswith("TAIL"))
        self.assertIn("truncated", stderr)
        self.assertTrue(stderr.endswith("ERRTAIL"))
        self.assertLessEqual(log_size, 128)
        self.assertIn(b"truncated", log_bytes)

    async def test_log_rotation_has_hysteresis_and_remains_bounded(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "bounded.log"
            path.write_bytes(b"")
            writer = furi_utils._BoundedLogWriter(path, 128)
            for _ in range(100):
                writer.append(b"01234567")
            rotations = writer.rotations
            writer.close()
            # Hysteresis prevents the former behavior of reading and rewriting
            # nearly the whole bounded log after every post-limit append.
            self.assertLessEqual(path.stat().st_size, 128)
            self.assertLess(rotations, 20)
            self.assertIn(b"truncated", path.read_bytes())


class ToolSafetyTests(unittest.IsolatedAsyncioTestCase):
    async def test_flash_defaults_to_dry_run(self) -> None:
        with patch.object(main, "run_command_async_stream", new=AsyncMock()) as runner:
            result = await main.flash_firmware()
        self.assertTrue(result["success"])
        self.assertTrue(result["dry_run"])
        self.assertFalse(result["executed"])
        runner.assert_not_awaited()

    async def test_flash_requires_confirmation(self) -> None:
        with patch.object(main, "run_command_async_stream", new=AsyncMock()) as runner:
            result = await main.flash_firmware(dry_run=False)
        self.assertEqual(result["return_code"], 2)
        runner.assert_not_awaited()

    async def test_flash_rejects_boolean_and_executes_only_with_exact_token(self) -> None:
        runner = AsyncMock(return_value=(0, "ok", ""))
        with patch.object(main, "run_command_async_stream", new=runner):
            rejected = await main.flash_firmware(confirm=True, dry_run=False)
            accepted = await main.flash_firmware(
                confirm=main.FLASH_FIRMWARE_CONFIRMATION, dry_run=False
            )
        self.assertEqual(rejected["error"], "validation_error")
        self.assertTrue(accepted["executed"])
        runner.assert_awaited_once()

    async def test_clean_rejects_boolean_and_executes_only_with_exact_token(self) -> None:
        runner = AsyncMock(return_value=(0, "ok", ""))
        with patch.object(main, "run_command_async_stream", new=runner):
            rejected = await main.clean_firmware(confirm=True, dry_run=False)
            accepted = await main.clean_firmware(
                confirm=main.CLEAN_FIRMWARE_CONFIRMATION, dry_run=False
            )
        self.assertEqual(rejected["error"], "validation_error")
        self.assertTrue(accepted["executed"])
        runner.assert_awaited_once()

    async def test_rejects_command_injection_in_app_id(self) -> None:
        with patch.object(main, "run_command_async_stream", new=AsyncMock()) as runner:
            result = await main.build_firmware(app_id="good;touch_bad")
        self.assertEqual(result["error"], "validation_error")
        runner.assert_not_awaited()

    async def test_build_uses_argv_and_target(self) -> None:
        runner = AsyncMock(return_value=(0, "ok", ""))
        with patch.object(main, "run_command_async_stream", new=runner):
            result = await main.build_firmware(target="f18", app_id="chip8")
        argv = runner.await_args.args[0]
        self.assertEqual(argv[1:], ["fap_chip8", "TARGET_HW=18"])
        self.assertTrue(result["success"])

    async def test_cli_defaults_to_plan_without_runner(self) -> None:
        with patch.object(main, "_cli", new=AsyncMock()) as runner:
            result = await main.flipper_cli("storage info; harmless")
        self.assertTrue(result["success"])
        self.assertTrue(result["dry_run"])
        self.assertFalse(result["executed"])
        self.assertEqual(result["required_confirmation"], main.FLIPPER_CLI_CONFIRMATION)
        runner.assert_not_awaited()

    async def test_cli_requires_exact_confirmation_without_runner(self) -> None:
        with patch.object(main, "_cli", new=AsyncMock()) as runner:
            result = await main.flipper_cli("storage info", dry_run=False, confirmation="yes")
        self.assertEqual(result["error"], "validation_error")
        self.assertFalse(result["executed"])
        runner.assert_not_awaited()

    async def test_cli_exact_confirmation_preserves_command_as_one_argument(self) -> None:
        runner = AsyncMock(return_value=(0, "ok", ""))
        with patch.object(main, "run_command_async", new=runner):
            result = await main.flipper_cli(
                "storage info; harmless",
                dry_run=False,
                confirmation=main.FLIPPER_CLI_CONFIRMATION,
            )
        argv = runner.await_args.args[0]
        self.assertEqual(argv[-1], "storage info; harmless")
        self.assertTrue(result["success"])
        self.assertTrue(result["executed"])

    async def test_gpio_set_defaults_to_plan_without_runner(self) -> None:
        with patch.object(main, "_cli", new=AsyncMock()) as runner:
            result = await main.gpio_set(3, True)
        self.assertTrue(result["dry_run"])
        self.assertFalse(result["executed"])
        runner.assert_not_awaited()

    async def test_gpio_set_requires_exact_confirmation_without_runner(self) -> None:
        with patch.object(main, "_cli", new=AsyncMock()) as runner:
            result = await main.gpio_set(3, True, dry_run=False, confirmation="yes")
        self.assertEqual(result["error"], "validation_error")
        runner.assert_not_awaited()

    async def test_gpio_set_executes_with_exact_confirmation(self) -> None:
        runner = AsyncMock(return_value=main._result(0, "ok", ""))
        with patch.object(main, "_cli", new=runner):
            result = await main.gpio_set(
                3,
                True,
                dry_run=False,
                confirmation=main.GPIO_SET_CONFIRMATION,
            )
        runner.assert_awaited_once_with("gpio set 3 1")
        self.assertTrue(result["executed"])

    async def test_gpio_parser_does_not_treat_pin_number_as_state(self) -> None:
        with patch.object(main, "_cli", new=AsyncMock(return_value=main._result(0, "GPIO 1 unavailable", ""))):
            result = await main.gpio_read(1)
        self.assertEqual(result["return_code"], 65)
        self.assertEqual(result["error"], "parse_error")

    async def test_gpio_parses_explicit_state(self) -> None:
        with patch.object(main, "_cli", new=AsyncMock(return_value=main._result(0, "GPIO 5 state: 1", ""))):
            result = await main.gpio_read(5)
        self.assertEqual(result["state"], "HIGH")

    async def test_devboard_tool_does_not_claim_deployment(self) -> None:
        result = await main.deploy_wifi_devboard_config()
        self.assertFalse(result["success"])
        self.assertFalse(result["executed"])
        self.assertEqual(result["error"], "not_implemented")


if __name__ == "__main__":
    unittest.main()
