import json
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from integration_server import EmulatorV2MCPServer


class MCPTests(unittest.TestCase):
    def setUp(self):
        self.server = EmulatorV2MCPServer()

    def test_initialize_and_tool_surface(self):
        response = self.server.handle_request({"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}})
        self.assertEqual(response["result"]["serverInfo"]["name"], "momentum-emulator-v2")
        tools = self.server.handle_request({"jsonrpc": "2.0", "id": 2, "method": "tools/list"})["result"]["tools"]
        names = {x["name"] for x in tools}
        self.assertTrue({"emulator_run", "emulator_events", "emulator_usb_rpc", "emulator_snapshot_metadata"} <= names)

    def test_native_surfaces_require_run_id(self):
        for name in ("emulator_screen", "emulator_input", "emulator_usb_rpc"):
            schema = {x["name"]: x["inputSchema"] for x in self.server.tools}[name]
            self.assertIn("run_id", schema["required"])

    def test_pb_main_semantic_decode(self):
        response = self.server._rpc_request(7, 6, b"ok")
        messages = self.server._decode_rpc_messages(response, "ping")
        self.assertEqual(messages[0]["command_id"], 7)
        self.assertEqual(messages[0]["content_tag"], 6)
        self.assertEqual(messages[0]["payload_bytes"], 2)
        self.assertTrue(messages[0]["success"])

    def test_stdio_has_only_jsonrpc_on_stdout(self):
        messages = "\n".join([
            json.dumps({"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}}),
            json.dumps({"jsonrpc": "2.0", "method": "notifications/initialized"}),
            json.dumps({"jsonrpc": "2.0", "id": 2, "method": "ping"}), ""])
        result = subprocess.run([sys.executable, str(HERE / "flipper_mcp_server.py")], input=messages, text=True, capture_output=True, check=True)
        lines = result.stdout.splitlines()
        self.assertEqual(len(lines), 2)
        self.assertTrue(all(json.loads(line)["jsonrpc"] == "2.0" for line in lines))

    def test_validate_spec(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); firmware = root / "fw.bin"; firmware.write_bytes(b"fw")
            spec = root / "spec.json"; spec.write_text(json.dumps({"firmware": str(firmware), "output": str(root / "out"), "inputs": [{"button": "OK", "action": "PRESS"}]}))
            result = self.server.call_tool("emulator_validate_spec", {"spec_path": str(spec)})
            self.assertTrue(result["valid"])
            self.assertEqual(result["inputs"], 1)

    def test_parse_error_is_jsonrpc(self):
        result = subprocess.run([sys.executable, str(HERE / "flipper_mcp_server.py")], input="{\n", text=True, capture_output=True, check=True)
        error = json.loads(result.stdout)
        self.assertEqual(error["error"]["code"], -32700)


if __name__ == "__main__": unittest.main()
