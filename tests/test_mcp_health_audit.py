import importlib.util
import json
import re
import sys
import tempfile
import textwrap
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
AUDIT_PATH = ROOT / ".ai/mcp/scripts/mcp_health_audit.py"
SPEC = importlib.util.spec_from_file_location("mcp_health_audit", AUDIT_PATH)
audit = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
sys.modules[SPEC.name] = audit
SPEC.loader.exec_module(audit)


class MCPHealthAuditTests(unittest.TestCase):
    IMPLEMENTATION_TEST_CONTRACT = {
        ".ai/claude-vscode/scripts/mcp_bridge.py": (
            "tests/test_mcp_bridges.py",
            "test_vscode_bridge_stdio_tools_list_and_flash_plan",
            "tests/test_mcp_bridges.py",
        ),
        ".ai/esp32_bridge/mcp_server.py": (
            ".ai/esp32_bridge/tests/test_bridge.py",
            "test_initialize_and_list_all_tools",
            ".ai/esp32_bridge",
        ),
        ".ai/mcp/scripts/a2a_server.py": (
            "tests/test_mcp_stdio.py",
            "test_a2a_server_initialize_and_lists_tools_without_mutating",
            "tests.test_mcp_stdio",
        ),
        ".ai/mcp/scripts/rag_server.py": (
            "tests/test_mcp_stdio.py",
            "test_rag_server_initialize_and_lists_tools_without_mutating",
            "tests.test_mcp_stdio",
        ),
        ".ai/mcp/scripts/repo_agent_server.py": (
            "tests/test_mcp_stdio.py",
            "test_repository_agent_lists_readonly_tools",
            "tests.test_mcp_stdio",
        ),
        ".ai/mcp/servers/esp_mcp/main.py": (
            "tests/test_mcp_stdio.py",
            "test_esp_server_fallback_lists_tools_without_sdk_or_device",
            "tests.test_mcp_stdio",
        ),
        ".ai/mcp/servers/flipper_recovery/main.py": (
            "tests/test_mcp_stdio.py",
            "test_recovery_server_fallback_lists_all_tools_without_device_access",
            "tests.test_mcp_stdio",
        ),
        ".ai/mcp/servers/strawberry_mcp/main.py": (
            "tests/test_mcp_stdio.py",
            "test_strawberry_server_fallback_lists_tools_without_sdk_or_device",
            "tests.test_mcp_stdio",
        ),
        ".ai/strawberry/src/strawberry/mcp_server.py": (
            "tests/test_strawberry_mcp.py",
            "test_dependency_free_server_initializes_and_lists_tools_without_credentials",
            "tests/test_strawberry_mcp.py",
        ),
        ".ai/tools/scripts/flipper_mcp.py": (
            "tests/test_mcp_stdio.py",
            "test_flipper_tools_lists_tools_without_device_access",
            "tests.test_mcp_stdio",
        ),
    }

    def test_repository_inventory_has_no_stale_local_paths(self):
        report = audit.audit(ROOT)
        self.assertGreaterEqual(report["registry_count"], 19)
        self.assertGreaterEqual(report["registration_count"], 52)
        self.assertEqual(report["invalid_configs"], [])
        broken = [
            (item["source"], item["name"], item["validation"]["issues"])
            for item in report["registrations"]
            if item["validation"]["issues"]
        ]
        self.assertEqual(broken, [])
        self.assertTrue(report["registry_references"])
        self.assertTrue(all(item["exists"] for item in report["registry_references"]))
        implementations = {item["path"]: item for item in report["implementation_inventory"]}
        self.assertEqual(len(implementations), 10)
        self.assertFalse(any("site-packages" in path for path in implementations))
        self.assertIn(".ai/esp32_bridge/mcp_server.py", implementations)
        self.assertIn(".ai/strawberry/src/strawberry/mcp_server.py", implementations)
        self.assertTrue(implementations[".ai/esp32_bridge/mcp_server.py"]["packaged"])
        self.assertTrue(implementations[".ai/strawberry/src/strawberry/mcp_server.py"]["packaged"])

    def test_every_implementation_has_a_safe_handshake_test_in_the_suite(self):
        """Keep implementation discovery and the hardware-free gate in lockstep."""
        report = audit.audit(ROOT)
        inventory = {item["path"] for item in report["implementation_inventory"]}
        self.assertEqual(set(self.IMPLEMENTATION_TEST_CONTRACT), inventory)

        suite_source = (ROOT / "scripts/test_mcp_suite.py").read_text(encoding="utf-8")
        for implementation, (test_path, test_name, suite_selector) in self.IMPLEMENTATION_TEST_CONTRACT.items():
            with self.subTest(implementation=implementation):
                test_file = ROOT / test_path
                self.assertTrue(test_file.is_file(), f"missing handshake test file for {implementation}")
                test_source = test_file.read_text(encoding="utf-8")
                self.assertRegex(
                    test_source,
                    rf"(?m)^\s*def\s+{re.escape(test_name)}\s*\(",
                    f"missing safe handshake/tools-list test for {implementation}",
                )
                self.assertIn(
                    suite_selector,
                    suite_source,
                    f"test suite does not execute the handshake test for {implementation}",
                )

    def test_health_probe_only_initializes_and_lists_tools(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            config_dir = root / ".ai/client"
            server_dir = root / ".ai/server"
            config_dir.mkdir(parents=True)
            server_dir.mkdir(parents=True)
            methods_path = root / "methods.json"
            server_path = server_dir / "server.py"
            server_path.write_text(
                textwrap.dedent(
                    f"""
                    import json
                    import sys
                    from pathlib import Path

                    seen = []
                    for line in sys.stdin:
                        request = json.loads(line)
                        seen.append(request.get("method"))
                        Path({str(methods_path)!r}).write_text(json.dumps(seen))
                        if request.get("id") is None:
                            continue
                        if request["method"] == "initialize":
                            result = {{"protocolVersion": "2024-11-05", "capabilities": {{"tools": {{}}}}, "serverInfo": {{"name": "test", "version": "1"}}}}
                        elif request["method"] == "tools/list":
                            result = {{"tools": [{{"name": "read_only", "inputSchema": {{"type": "object"}}}}]}}
                        else:
                            raise RuntimeError("unexpected method")
                        print(json.dumps({{"jsonrpc": "2.0", "id": request["id"], "result": result}}), flush=True)
                    """
                ),
                encoding="utf-8",
            )
            (config_dir / "mcp.json").write_text(
                json.dumps(
                    {
                        "mcpServers": {
                            "safe": {
                                "command": sys.executable,
                                "args": [str(server_path.relative_to(root))],
                            }
                        }
                    }
                ),
                encoding="utf-8",
            )
            report = audit.audit(root, health=True, timeout=2)
            health = report["registrations"][0]["health"]
            self.assertEqual(health["status"], "healthy")
            self.assertEqual(health["tool_count"], 1)
            self.assertEqual(
                json.loads(methods_path.read_text()),
                ["initialize", "notifications/initialized", "tools/list"],
            )

    def test_external_and_remote_servers_are_not_started(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            config_dir = root / ".ai"
            config_dir.mkdir()
            (config_dir / "mcp.json").write_text(
                json.dumps(
                    {
                        "mcpServers": {
                            "remote": {"url": "https://example.invalid/mcp"},
                            "package": {"command": "npx", "args": ["-y", "example-package"]},
                        }
                    }
                ),
                encoding="utf-8",
            )
            report = audit.audit(root, health=True, timeout=0.1)
            statuses = {item["name"]: item["health"]["status"] for item in report["registrations"]}
            self.assertEqual(statuses["remote"], "remote_not_probed")
            self.assertEqual(statuses["package"], "external_not_probed")
            self.assertFalse(audit.report_has_failures(report, health=True))

    def test_health_probe_uses_configured_environment_without_reporting_values(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            config_dir = root / ".ai"
            config_dir.mkdir()
            server = config_dir / "env_server.py"
            server.write_text(
                textwrap.dedent(
                    """
                    import json, os, sys
                    if os.environ.get("REQUIRED_SETTING") != "works":
                        raise SystemExit(2)
                    for line in sys.stdin:
                        request = json.loads(line)
                        if "id" not in request:
                            continue
                        result = (
                            {"protocolVersion":"2024-11-05","capabilities":{"tools":{}},"serverInfo":{"name":"env","version":"1"}}
                            if request["method"] == "initialize" else {"tools": [{"name": "ready", "inputSchema": {"type": "object"}}]}
                        )
                        print(json.dumps({"jsonrpc":"2.0","id":request["id"],"result":result}), flush=True)
                    """
                ),
                encoding="utf-8",
            )
            (config_dir / "mcp.json").write_text(
                json.dumps(
                    {
                        "mcpServers": {
                            "env": {
                                "command": sys.executable,
                                "args": [str(server.relative_to(root))],
                                "env": {"REQUIRED_SETTING": "works", "SECRET_VALUE": "do-not-report"},
                            }
                        }
                    }
                ),
                encoding="utf-8",
            )
            report = audit.audit(root, health=True, timeout=2)
            row = report["registrations"][0]
            self.assertEqual(row["health"]["status"], "healthy")
            self.assertEqual(row["env_keys"], ["REQUIRED_SETTING", "SECRET_VALUE"])
            self.assertNotIn("do-not-report", json.dumps(report))

    def test_health_rejects_empty_malformed_and_duplicate_tool_lists(self):
        invalid_lists = [
            ([], "tools must not be empty"),
            ([{"name": "", "inputSchema": {"type": "object"}}], "non-empty string name"),
            ([{"name": "one"}], "object inputSchema"),
            (
                [
                    {"name": "same", "inputSchema": {"type": "object"}},
                    {"name": "same", "inputSchema": {"type": "object"}},
                ],
                "duplicate tool name",
            ),
        ]
        for tools, expected_error in invalid_lists:
            with self.subTest(tools=tools), tempfile.TemporaryDirectory() as temp_dir:
                root = Path(temp_dir)
                config_dir = root / ".ai"
                config_dir.mkdir()
                server = config_dir / "invalid_tools.py"
                server.write_text(
                    textwrap.dedent(
                        f"""
                        import json, sys
                        tools = {tools!r}
                        for line in sys.stdin:
                            request = json.loads(line)
                            if "id" not in request:
                                continue
                            result = (
                                {{"protocolVersion":"2024-11-05","capabilities":{{"tools":{{}}}},"serverInfo":{{"name":"invalid","version":"1"}}}}
                                if request["method"] == "initialize" else {{"tools": tools}}
                            )
                            print(json.dumps({{"jsonrpc":"2.0","id":request["id"],"result":result}}), flush=True)
                        """
                    ),
                    encoding="utf-8",
                )
                (config_dir / "mcp.json").write_text(
                    json.dumps({"mcpServers": {"invalid": {"command": sys.executable, "args": [str(server.relative_to(root))]}}}),
                    encoding="utf-8",
                )
                report = audit.audit(root, health=True, timeout=2)
                health = report["registrations"][0]["health"]
                self.assertEqual(health["status"], "tools_list_invalid")
                self.assertIn(expected_error, health["error"])
                self.assertTrue(audit.report_has_failures(report, health=True))

    def test_noisy_stderr_cannot_deadlock_health_probe(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            config_dir = root / ".ai"
            config_dir.mkdir()
            server = config_dir / "noisy.py"
            server.write_text(
                textwrap.dedent(
                    """
                    import json, sys
                    sys.stderr.write("x" * 2_000_000)
                    sys.stderr.flush()
                    for line in sys.stdin:
                        request = json.loads(line)
                        if "id" not in request:
                            continue
                        result = (
                            {"protocolVersion":"2024-11-05","capabilities":{"tools":{}},"serverInfo":{"name":"noisy","version":"1"}}
                            if request["method"] == "initialize" else
                            {"tools":[{"name":"ready","inputSchema":{"type":"object"}}]}
                        )
                        print(json.dumps({"jsonrpc":"2.0","id":request["id"],"result":result}), flush=True)
                    """
                ),
                encoding="utf-8",
            )
            (config_dir / "mcp.json").write_text(
                json.dumps({"mcpServers": {"noisy": {"command": sys.executable, "args": [str(server.relative_to(root))]}}}),
                encoding="utf-8",
            )
            report = audit.audit(root, health=True, timeout=2)
            self.assertEqual(report["registrations"][0]["health"]["status"], "healthy")

    def test_missing_local_target_is_a_failure(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            config_dir = root / ".ai"
            config_dir.mkdir()
            (config_dir / "mcp.json").write_text(
                json.dumps(
                    {
                        "mcpServers": {
                            "broken": {
                                "command": sys.executable,
                                "args": [".ai/missing.py"],
                            }
                        }
                    }
                ),
                encoding="utf-8",
            )
            report = audit.audit(root)
            self.assertEqual(report["registrations"][0]["validation"]["issues"], ["local_target_not_found"])
            self.assertTrue(audit.report_has_failures(report))


if __name__ == "__main__":
    unittest.main()
