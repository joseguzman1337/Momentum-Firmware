import importlib.util
import asyncio
import json
import subprocess
import sys
import tempfile
import threading
import unittest
from pathlib import Path
from typing import Optional
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
RUNTIME_PATH = ROOT / ".ai/mcp/scripts/mcp_stdio.py"
SPEC = importlib.util.spec_from_file_location("mcp_stdio", RUNTIME_PATH)
mcp_stdio = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(mcp_stdio)


class MCPStdioRuntimeTests(unittest.TestCase):
    def server(self):
        server = mcp_stdio.MCPStdioServer("test")
        server.tool(
            "echo",
            "Echo text",
            {"type": "object", "properties": {"text": {"type": "string"}}, "required": ["text"]},
            lambda text: {"text": text},
        )
        return server

    def test_oversized_unterminated_line_is_drained_before_next_request(self):
        script = (
            "import importlib.util;"
            f"s=importlib.util.spec_from_file_location('runtime',{str(RUNTIME_PATH)!r});"
            "m=importlib.util.module_from_spec(s);s.loader.exec_module(m);"
            "m.MCPStdioServer('bounded').run()"
        )
        valid = b'{"jsonrpc":"2.0","id":7,"method":"ping"}\n'
        completed = subprocess.run(
            [sys.executable, "-c", script],
            input=b"X" * (mcp_stdio.MAX_REQUEST_BYTES + 4096) + b"\n" + valid,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=10,
            check=True,
        )
        responses = [json.loads(line) for line in completed.stdout.splitlines()]
        self.assertEqual(responses[0]["error"]["message"], "Request too large")
        self.assertEqual(responses[1], {"jsonrpc": "2.0", "id": 7, "result": {}})

    def test_initialize_and_tools_list_are_protocol_compliant(self):
        server = self.server()
        initialized = server.dispatch({"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}})
        self.assertEqual(initialized["id"], 1)
        self.assertIn("protocolVersion", initialized["result"])
        tools = server.dispatch({"jsonrpc": "2.0", "id": 2, "method": "tools/list"})
        self.assertEqual([tool["name"] for tool in tools["result"]["tools"]], ["echo"])
        null_id = server.dispatch({"jsonrpc": "2.0", "id": None, "method": "ping"})
        self.assertIn("result", null_id)
        self.assertIsNone(null_id["id"])
        self.assertIsNone(server.dispatch({"jsonrpc": "2.0", "method": "ping"}))

    def test_tool_call_and_standard_errors(self):
        server = self.server()
        result = server.dispatch(
            {"jsonrpc": "2.0", "id": 3, "method": "tools/call", "params": {"name": "echo", "arguments": {"text": "ok"}}}
        )
        self.assertFalse(result["result"]["isError"])
        unknown = server.dispatch({"jsonrpc": "2.0", "id": 4, "method": "missing"})
        self.assertEqual(unknown["error"]["code"], -32601)

    def test_tool_schema_is_enforced_before_handler(self):
        calls = []
        server = mcp_stdio.MCPStdioServer("schema-test")
        server.tool(
            "bounded",
            "bounded input",
            {
                "type": "object",
                "properties": {
                    "name": {"type": "string", "minLength": 2, "maxLength": 4, "pattern": "^[a-z]+$"},
                    "count": {"type": "integer", "minimum": 1, "maximum": 3},
                },
                "required": ["name", "count"],
                "additionalProperties": False,
            },
            lambda **kwargs: calls.append(kwargs),
        )
        invalid_requests = [
            {"name": "A", "count": 1},
            {"name": "abcd", "count": 4},
            {"name": "ab", "count": True},
            {"name": "ab", "count": 1, "extra": 1},
        ]
        for request_id, arguments in enumerate(invalid_requests, start=1):
            response = server.dispatch(
                {"jsonrpc": "2.0", "id": request_id, "method": "tools/call", "params": {"name": "bounded", "arguments": arguments}}
            )
            self.assertEqual(response["error"]["code"], -32602)
        self.assertEqual(calls, [])
        response = server.dispatch(
            {"jsonrpc": "2.0", "id": 10, "method": "tools/call", "params": {"name": "bounded", "arguments": {"name": "abc", "count": 2}}}
        )
        self.assertFalse(response["result"]["isError"])
        self.assertEqual(calls, [{"name": "abc", "count": 2}])

    def test_async_handler_is_supported_by_fallback_runtime(self):
        server = mcp_stdio.MCPStdioServer("async-test")

        async def handler(value: int):
            await asyncio.sleep(0)
            return {"value": value}

        server.tool(
            "async_echo",
            "async echo",
            {
                "type": "object",
                "properties": {"value": {"type": "integer"}},
                "required": ["value"],
                "additionalProperties": False,
            },
            handler,
        )
        response = server.dispatch(
            {"jsonrpc": "2.0", "id": 1, "method": "tools/call", "params": {"name": "async_echo", "arguments": {"value": 7}}}
        )
        self.assertFalse(response["result"]["isError"])
        self.assertIn('"value": 7', response["result"]["content"][0]["text"])

    def test_fallback_schema_resolves_bool_int_optional_and_containers(self):
        compat = mcp_stdio.FastMCPCompat("typing-test")

        @compat.tool()
        def typed(pin: int, enabled: bool, names: list[str], note: Optional[str] = None):
            return {"pin": pin, "enabled": enabled, "names": names, "note": note}

        schema = compat.server._tools["typed"][0]["inputSchema"]
        self.assertEqual(schema["properties"]["pin"], {"type": "integer"})
        self.assertEqual(schema["properties"]["enabled"], {"type": "boolean"})
        self.assertEqual(schema["properties"]["names"], {"type": "array", "items": {"type": "string"}})
        self.assertEqual(
            schema["properties"]["note"],
            {"anyOf": [{"type": "string"}, {"type": "null"}]},
        )
        result = compat.server.dispatch(
            {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "tools/call",
                "params": {"name": "typed", "arguments": {"pin": 3, "enabled": True, "names": ["a"]}},
            }
        )
        self.assertFalse(result["result"]["isError"])
        explicit_null = compat.server.dispatch(
            {
                "jsonrpc": "2.0",
                "id": 2,
                "method": "tools/call",
                "params": {
                    "name": "typed",
                    "arguments": {"pin": 3, "enabled": True, "names": ["a"], "note": None},
                },
            }
        )
        self.assertFalse(explicit_null["result"]["isError"])
        wrong_optional_type = compat.server.dispatch(
            {
                "jsonrpc": "2.0",
                "id": 3,
                "method": "tools/call",
                "params": {
                    "name": "typed",
                    "arguments": {"pin": 3, "enabled": True, "names": ["a"], "note": 7},
                },
            }
        )
        self.assertEqual(wrong_optional_type["error"]["code"], -32602)

    def test_rag_server_initialize_and_lists_tools_without_mutating(self):
        self.assert_server_lists_tools(
            ROOT / ".ai/mcp/scripts/rag_server.py",
            {"query_knowledge", "query", "reindex_knowledge", "reindex"},
        )

    def test_rag_legacy_aliases_share_handlers_and_schemas(self):
        module = self.load_module(ROOT / ".ai/mcp/scripts/rag_server.py", "test_rag_aliases")
        with tempfile.TemporaryDirectory() as directory:
            knowledge_base = Path(directory) / "knowledge.json"
            knowledge_base.write_text(json.dumps({"notes": "legacy needle"}), encoding="utf-8")
            with mock.patch.dict(
                "os.environ", {"REPO_ROOT": directory, "KNOWLEDGE_BASE": str(knowledge_base)}
            ):
                mcp = module.create_mcp_server(module.RAGServer())
            for current, legacy in (("query_knowledge", "query"), ("reindex_knowledge", "reindex")):
                self.assertIs(mcp._tools[current][0]["inputSchema"], mcp._tools[legacy][0]["inputSchema"])
                self.assertIs(mcp._tools[current][1], mcp._tools[legacy][1])
            self.assertIn("mutating", mcp._tools["reindex"][0]["description"])
            response = mcp.dispatch(
                {
                    "jsonrpc": "2.0",
                    "id": 1,
                    "method": "tools/call",
                    "params": {"name": "query", "arguments": {"query": "needle"}},
                }
            )
            self.assertFalse(response["result"]["isError"])
            self.assertIn("legacy needle", response["result"]["content"][0]["text"])

    def test_rag_reindex_is_atomic_and_query_rejects_oversized_index(self):
        rag_path = ROOT / ".ai/mcp/scripts/rag_server.py"
        spec = importlib.util.spec_from_file_location("test_rag_server", rag_path)
        module = importlib.util.module_from_spec(spec)
        assert spec and spec.loader
        sys.path.insert(0, str(rag_path.parent))
        try:
            spec.loader.exec_module(module)
        finally:
            sys.path.pop(0)
        with tempfile.TemporaryDirectory() as directory:
            with mock.patch.dict(
                "os.environ",
                {"REPO_ROOT": directory, "KNOWLEDGE_BASE": str(Path(directory) / "nested/knowledge.json")},
            ):
                server = module.RAGServer()
            with mock.patch.object(server, "get_recent_commits", return_value=[]), mock.patch.object(
                server, "get_open_issues", return_value=[]
            ):
                indexed = server.index_knowledge()
            self.assertIsInstance(indexed, dict)
            self.assertTrue(server.knowledge_base.is_file())
            server.knowledge_base.write_bytes(b"{" + b" " * (10 * 1024 * 1024))
            with self.assertRaisesRegex(ValueError, "10 MiB"):
                server.query("test")

    def assert_server_lists_tools(self, path, expected):
        process = subprocess.Popen(
            [sys.executable, str(path)],
            cwd=ROOT,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        try:
            requests = [
                {"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}},
                {"jsonrpc": "2.0", "method": "notifications/initialized"},
                {"jsonrpc": "2.0", "id": 2, "method": "tools/list"},
            ]
            stdout, stderr = process.communicate(
                "".join(json.dumps(item) + "\n" for item in requests), timeout=5
            )
        finally:
            if process.poll() is None:
                process.kill()
        responses = [json.loads(line) for line in stdout.splitlines()]
        self.assertEqual([item["id"] for item in responses], [1, 2])
        self.assertEqual({tool["name"] for tool in responses[1]["result"]["tools"]}, expected)
        self.assertEqual(stderr, "")

    def load_module(self, path, name):
        spec = importlib.util.spec_from_file_location(name, path)
        module = importlib.util.module_from_spec(spec)
        assert spec and spec.loader
        sys.path.insert(0, str(path.parent))
        try:
            spec.loader.exec_module(module)
        finally:
            sys.path.pop(0)
        return module

    def test_a2a_server_initialize_and_lists_tools_without_mutating(self):
        self.assert_server_lists_tools(
            ROOT / ".ai/mcp/scripts/a2a_server.py",
            {"get_messages", "send_message", "send", "mark_read", "broadcast", "coordinate_task", "coordinate"},
        )

    def test_a2a_legacy_aliases_share_handlers_and_schemas(self):
        module = self.load_module(ROOT / ".ai/mcp/scripts/a2a_server.py", "test_a2a_aliases")
        with tempfile.TemporaryDirectory() as directory, mock.patch.dict(
            "os.environ", {"REPO_ROOT": directory, "MESSAGE_BUS": str(Path(directory) / "bus.json")}
        ):
            mcp = module.create_mcp_server(module.A2AServer())
            for current, legacy in (("send_message", "send"), ("coordinate_task", "coordinate")):
                self.assertIs(mcp._tools[current][0]["inputSchema"], mcp._tools[legacy][0]["inputSchema"])
                self.assertIs(mcp._tools[current][1], mcp._tools[legacy][1])
                self.assertIn("mutating", mcp._tools[legacy][0]["description"])
            send_response = mcp.dispatch(
                {
                    "jsonrpc": "2.0",
                    "id": 1,
                    "method": "tools/call",
                    "params": {
                        "name": "send",
                        "arguments": {
                            "from_agent": "legacy",
                            "to_agent": "target",
                            "message_type": "test",
                            "payload": {"safe": True},
                        },
                    },
                }
            )
            self.assertFalse(send_response["result"]["isError"])
            coordinate_response = mcp.dispatch(
                {
                    "jsonrpc": "2.0",
                    "id": 2,
                    "method": "tools/call",
                    "params": {
                        "name": "coordinate",
                        "arguments": {"task": {"id": "legacy-test", "assigned_to": "codex", "type": "test"}},
                    },
                }
            )
            self.assertFalse(coordinate_response["result"]["isError"])

    def test_a2a_concurrent_writers_keep_unique_messages(self):
        server_path = ROOT / ".ai/mcp/scripts/a2a_server.py"
        spec = importlib.util.spec_from_file_location("test_a2a_server", server_path)
        module = importlib.util.module_from_spec(spec)
        assert spec and spec.loader
        sys.path.insert(0, str(server_path.parent))
        try:
            spec.loader.exec_module(module)
        finally:
            sys.path.pop(0)
        with tempfile.TemporaryDirectory() as directory:
            bus = Path(directory) / "message_bus.json"
            with mock.patch.dict("os.environ", {"REPO_ROOT": directory, "MESSAGE_BUS": str(bus)}):
                servers = [module.A2AServer(), module.A2AServer()]
            barrier = threading.Barrier(2)
            errors = []

            def send(server, sender):
                try:
                    barrier.wait()
                    server.send_message(sender, "target", "test", {"sender": sender})
                except Exception as error:  # pragma: no cover - assertion reports details
                    errors.append(error)

            threads = [threading.Thread(target=send, args=(server, f"agent-{index}")) for index, server in enumerate(servers)]
            for thread in threads:
                thread.start()
            for thread in threads:
                thread.join(timeout=5)
            self.assertEqual(errors, [])
            messages = json.loads(bus.read_text(encoding="utf-8"))
            self.assertEqual(len(messages), 2)
            self.assertEqual({item["id"] for item in messages}, {1, 2})

    def test_a2a_concurrent_broadcasts_commit_complete_unique_batches(self):
        module = self.load_a2a_module()
        with tempfile.TemporaryDirectory() as directory:
            bus = Path(directory) / "message_bus.json"
            bus.write_text(json.dumps({"messages": [], "last_updated": "legacy"}), encoding="utf-8")
            with mock.patch.dict("os.environ", {"REPO_ROOT": directory, "MESSAGE_BUS": str(bus)}):
                servers = [module.A2AServer(), module.A2AServer()]
            barrier = threading.Barrier(2)
            errors = []

            def broadcast(server, sender):
                try:
                    barrier.wait()
                    server.broadcast(sender, "test", {"sender": sender})
                except Exception as error:  # pragma: no cover - assertion reports details
                    errors.append(error)

            threads = [
                threading.Thread(target=broadcast, args=(server, sender))
                for server, sender in zip(servers, ("codex", "claude"))
            ]
            for thread in threads:
                thread.start()
            for thread in threads:
                thread.join(timeout=5)

            document = json.loads(bus.read_text(encoding="utf-8"))
            messages = document["messages"]
            self.assertEqual(errors, [])
            self.assertEqual(len(messages), 8)
            self.assertEqual({item["id"] for item in messages}, set(range(1, 9)))
            self.assertEqual(
                {sender: sum(item["from"] == sender for item in messages) for sender in ("codex", "claude")},
                {"codex": 4, "claude": 4},
            )
            self.assertIn("last_updated", document)

    def test_a2a_broadcast_replace_failure_never_persists_partial_batch(self):
        module = self.load_a2a_module()
        with tempfile.TemporaryDirectory() as directory:
            bus = Path(directory) / "message_bus.json"
            original = {"messages": [{"id": 9, "to": "codex"}], "last_updated": "legacy"}
            bus.write_text(json.dumps(original), encoding="utf-8")
            with mock.patch.dict("os.environ", {"REPO_ROOT": directory, "MESSAGE_BUS": str(bus)}):
                server = module.A2AServer()
            with mock.patch.object(module.os, "replace", side_effect=OSError("injected replace failure")):
                with self.assertRaisesRegex(OSError, "injected replace failure"):
                    server.broadcast("orchestrator", "test", {"value": 1})
            self.assertEqual(json.loads(bus.read_text(encoding="utf-8")), original)
            self.assertEqual(list(Path(directory).glob(".message-bus.*")), [])

    def load_a2a_module(self):
        server_path = ROOT / ".ai/mcp/scripts/a2a_server.py"
        spec = importlib.util.spec_from_file_location("test_a2a_server_batch", server_path)
        module = importlib.util.module_from_spec(spec)
        assert spec and spec.loader
        sys.path.insert(0, str(server_path.parent))
        try:
            spec.loader.exec_module(module)
        finally:
            sys.path.pop(0)
        return module

    def test_recovery_server_fallback_lists_all_tools_without_device_access(self):
        self.assert_server_lists_tools(
            ROOT / ".ai/mcp/servers/flipper_recovery/main.py",
            {
                "get_recovery_status",
                "analyze_firmware_image",
                "get_verified_good_state",
                "run_safe_build",
                "flash_firmware_usb",
                "flash_firmware_swd",
                "recover_to_good_state",
                "arm_autoflash",
                "get_monitor_observation",
                "run_monitor_once",
                "start_recovery_monitor",
                "stop_recovery_monitor",
                "get_monitor_status",
                "get_monitor_history",
                "get_monitor_debug_summary",
            },
        )

    def test_flipper_tools_lists_tools_without_device_access(self):
        self.assert_server_lists_tools(
            ROOT / ".ai/tools/scripts/flipper_mcp.py",
            {"build_firmware", "flash_firmware", "launch_app", "get_available_tools"},
        )

    def test_flipper_launch_defaults_to_hardware_free_dry_run(self):
        server_path = ROOT / ".ai/tools/scripts/flipper_mcp.py"
        spec = importlib.util.spec_from_file_location("test_flipper_tools", server_path)
        module = importlib.util.module_from_spec(spec)
        assert spec and spec.loader
        spec.loader.exec_module(module)
        tools = module.FlipperToolsMCP()

        with mock.patch.object(module.subprocess, "run") as run:
            result = tools.launch_app("applications/external/example")
        run.assert_not_called()
        self.assertTrue(result["dry_run"])
        self.assertIn("APPSRC=applications/external/example", result["command"])

    def test_flipper_launch_requires_exact_confirmation_before_subprocess(self):
        server_path = ROOT / ".ai/tools/scripts/flipper_mcp.py"
        spec = importlib.util.spec_from_file_location("test_flipper_tools_confirm", server_path)
        module = importlib.util.module_from_spec(spec)
        assert spec and spec.loader
        spec.loader.exec_module(module)
        tools = module.FlipperToolsMCP()

        with mock.patch.object(module.subprocess, "run") as run:
            with self.assertRaisesRegex(PermissionError, module.LAUNCH_CONFIRM):
                tools.launch_app("applications/external/example", confirm="almost", dry_run=False)
        run.assert_not_called()

    def test_flipper_launch_capability_remains_available_after_confirmation(self):
        server_path = ROOT / ".ai/tools/scripts/flipper_mcp.py"
        spec = importlib.util.spec_from_file_location("test_flipper_tools_enabled", server_path)
        module = importlib.util.module_from_spec(spec)
        assert spec and spec.loader
        spec.loader.exec_module(module)
        tools = module.FlipperToolsMCP()
        completed = subprocess.CompletedProcess(args=[], returncode=0, stdout="ok", stderr="")

        with mock.patch.object(module.subprocess, "run", return_value=completed) as run:
            result = tools.launch_app(
                "applications/external/example",
                confirm=module.LAUNCH_CONFIRM,
                dry_run=False,
            )
        run.assert_called_once()
        self.assertTrue(result["success"])

    def test_flipper_flash_dry_run_requires_exact_confirmation_without_subprocess(self):
        server_path = ROOT / ".ai/tools/scripts/flipper_mcp.py"
        spec = importlib.util.spec_from_file_location("test_flipper_flash_gate", server_path)
        module = importlib.util.module_from_spec(spec)
        assert spec and spec.loader
        spec.loader.exec_module(module)
        tools = module.FlipperToolsMCP()

        with mock.patch.object(module.subprocess, "run") as run:
            with self.assertRaisesRegex(PermissionError, module.CONFIRM):
                tools.flash_firmware(confirm="almost")
            plan = tools.flash_firmware(confirm=module.CONFIRM)
        run.assert_not_called()
        self.assertTrue(plan["dry_run"])
        self.assertIn("flash_usb_full", plan["command"])

    def test_flipper_flash_capability_executes_only_after_confirmation(self):
        server_path = ROOT / ".ai/tools/scripts/flipper_mcp.py"
        spec = importlib.util.spec_from_file_location("test_flipper_flash_enabled", server_path)
        module = importlib.util.module_from_spec(spec)
        assert spec and spec.loader
        spec.loader.exec_module(module)
        tools = module.FlipperToolsMCP()
        completed = subprocess.CompletedProcess(args=[], returncode=0, stdout="ok", stderr="")

        with mock.patch.object(module.subprocess, "run", return_value=completed) as run:
            result = tools.flash_firmware(
                confirm=module.CONFIRM,
                dry_run=False,
            )
        run.assert_called_once()
        self.assertTrue(result["success"])

    def test_flipper_build_rejects_unknown_target_before_subprocess(self):
        server_path = ROOT / ".ai/tools/scripts/flipper_mcp.py"
        spec = importlib.util.spec_from_file_location("test_flipper_build_target", server_path)
        module = importlib.util.module_from_spec(spec)
        assert spec and spec.loader
        spec.loader.exec_module(module)
        tools = module.FlipperToolsMCP()

        with mock.patch.object(module.subprocess, "run") as run:
            with self.assertRaisesRegex(ValueError, "target must be"):
                tools.build_firmware("invalid")
        run.assert_not_called()

    def test_esp_server_fallback_lists_tools_without_sdk_or_device(self):
        self.assert_server_lists_tools(
            ROOT / ".ai/mcp/servers/esp_mcp/main.py",
            {
                "build_esp_project",
                "setup_project_esp_target",
                "create_esp_project",
                "flash_esp_project",
                "list_esp_serial_ports",
                "run_esp_idf_install",
                "run_pytest",
            },
        )

    def test_esp_nullable_parameters_are_advertised_as_nullable(self):
        path = ROOT / ".ai/mcp/servers/esp_mcp/main.py"
        process = subprocess.run(
            [sys.executable, str(path)],
            cwd=ROOT,
            input=json.dumps({"jsonrpc": "2.0", "id": 1, "method": "tools/list"}) + "\n",
            capture_output=True,
            text=True,
            timeout=5,
            check=False,
        )
        response = json.loads(process.stdout)
        tools = {tool["name"]: tool for tool in response["result"]["tools"]}
        checks = {
            "build_esp_project": ("idf_path", "sdkconfig_defaults"),
            "setup_project_esp_target": ("idf_path",),
            "run_esp_idf_install": ("idf_path",),
            "run_pytest": ("idf_path",),
        }
        for tool_name, fields in checks.items():
            for field in fields:
                alternatives = tools[tool_name]["inputSchema"]["properties"][field]["anyOf"]
                self.assertIn({"type": "null"}, alternatives)

    def test_esp_command_failure_is_mcp_tool_error(self):
        server_dir = ROOT / ".ai/mcp/servers/esp_mcp"
        spec = importlib.util.spec_from_file_location("test_esp_mcp_failure", server_dir / "main.py")
        module = importlib.util.module_from_spec(spec)
        assert spec and spec.loader
        sys.path.insert(0, str(server_dir))
        try:
            spec.loader.exec_module(module)
        finally:
            sys.path.pop(0)
        with tempfile.TemporaryDirectory() as project, tempfile.TemporaryDirectory() as logs, mock.patch.object(
            module, "LOG_DIR", logs
        ), mock.patch.object(module, "get_export_script", return_value="/idf/export.sh"), mock.patch.object(
            module, "run_command_async_stream", new=mock.AsyncMock(return_value=(7, "", "build failed"))
        ):
            response = module.mcp.server.dispatch(
                {
                    "jsonrpc": "2.0",
                    "id": 1,
                    "method": "tools/call",
                    "params": {"name": "build_esp_project", "arguments": {"project_path": project, "idf_path": None}},
                }
            )
        self.assertTrue(response["result"]["isError"])
        self.assertIn("exit code 7", response["result"]["content"][0]["text"])

    def test_strawberry_server_fallback_lists_tools_without_sdk_or_device(self):
        self.assert_server_lists_tools(
            ROOT / ".ai/mcp/servers/strawberry_mcp/main.py",
            {
                "build_firmware",
                "flash_firmware",
                "clean_firmware",
                "deploy_wifi_devboard_config",
                "gpio_set",
                "gpio_read",
                "system_info",
                "storage_info",
                "nfc_detect",
                "flipper_cli",
            },
        )

    def test_repository_agent_lists_readonly_tools(self):
        self.assert_server_lists_tools(
            ROOT / ".ai/mcp/scripts/repo_agent_server.py",
            {"get_repository_summary", "validate_workspace", "list_capabilities"},
        )
