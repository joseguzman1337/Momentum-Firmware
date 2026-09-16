import asyncio
import importlib.util
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
SERVER_DIR = ROOT / ".ai/mcp/servers/esp_mcp"


def _load_server(name: str):
    spec = importlib.util.spec_from_file_location(name, SERVER_DIR / "main.py")
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    sys.path.insert(0, str(SERVER_DIR))
    try:
        spec.loader.exec_module(module)
    finally:
        sys.path.pop(0)
    return module


class EspInstallGateTests(unittest.TestCase):
    def setUp(self):
        self.module = _load_server(f"esp_install_gate_{id(self)}")

    @staticmethod
    def _idf_root(parent: str, name: str = "esp-idf") -> Path:
        root = Path(parent) / name
        root.mkdir()
        (root / "install.sh").write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
        return root

    def test_untrusted_caller_selected_root_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            trusted = self._idf_root(directory, "trusted")
            untrusted = self._idf_root(directory, "untrusted")
            env = {"ESP_MCP_TRUSTED_IDF_ROOTS": str(trusted)}
            with mock.patch.dict(os.environ, env, clear=True), mock.patch.object(
                self.module, "run_command_async_stream", new=mock.AsyncMock()
            ) as run:
                with self.assertRaisesRegex(PermissionError, "not trusted"):
                    asyncio.run(self.module.run_esp_idf_install(str(untrusted)))
            run.assert_not_awaited()

    def test_symlinked_install_script_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "esp-idf"
            root.mkdir()
            target = Path(directory) / "real-install.sh"
            target.write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
            (root / "install.sh").symlink_to(target)
            with mock.patch.dict(
                os.environ, {"ESP_MCP_TRUSTED_IDF_ROOTS": str(root)}, clear=True
            ), mock.patch.object(
                self.module, "run_command_async_stream", new=mock.AsyncMock()
            ) as run:
                with self.assertRaisesRegex(PermissionError, "symlinked"):
                    asyncio.run(self.module.run_esp_idf_install(str(root)))
            run.assert_not_awaited()

    def test_execution_requires_exact_confirmation(self):
        with tempfile.TemporaryDirectory() as directory:
            root = self._idf_root(directory)
            with mock.patch.dict(
                os.environ, {"ESP_MCP_TRUSTED_IDF_ROOTS": str(root)}, clear=True
            ), mock.patch.object(
                self.module, "run_command_async_stream", new=mock.AsyncMock()
            ) as run:
                with self.assertRaisesRegex(PermissionError, self.module.INSTALL_CONFIRMATION):
                    asyncio.run(
                        self.module.run_esp_idf_install(
                            str(root), confirm="almost", dry_run=False
                        )
                    )
            run.assert_not_awaited()

    def test_default_is_validated_dry_run(self):
        with tempfile.TemporaryDirectory() as directory:
            root = self._idf_root(directory)
            with mock.patch.dict(
                os.environ, {"ESP_MCP_TRUSTED_IDF_ROOTS": str(root)}, clear=True
            ), mock.patch.object(
                self.module, "run_command_async_stream", new=mock.AsyncMock()
            ) as run:
                stdout, stderr = asyncio.run(self.module.run_esp_idf_install(str(root)))
            run.assert_not_awaited()
            self.assertEqual(stdout, "")
            self.assertIn("Dry run only", stderr)

    def test_exact_confirmation_runs_validated_script(self):
        with tempfile.TemporaryDirectory() as directory, tempfile.TemporaryDirectory() as logs:
            root = self._idf_root(directory)
            runner = mock.AsyncMock(return_value=(0, "installed", ""))
            with mock.patch.dict(
                os.environ, {"ESP_MCP_TRUSTED_IDF_ROOTS": str(root)}, clear=True
            ), mock.patch.object(self.module, "LOG_DIR", logs), mock.patch.object(
                self.module, "run_command_async_stream", new=runner
            ):
                stdout, stderr = asyncio.run(
                    self.module.run_esp_idf_install(
                        str(root),
                        confirm=self.module.INSTALL_CONFIRMATION,
                        dry_run=False,
                    )
                )
            runner.assert_awaited_once()
            args, kwargs = runner.await_args
            resolved_root = root.resolve()
            self.assertEqual(args[0], ["bash", str(resolved_root / "install.sh")])
            self.assertEqual(kwargs["cwd"], str(resolved_root))
            self.assertIn("installed", stdout)
            self.assertEqual(stderr, "")


if __name__ == "__main__":
    unittest.main()
