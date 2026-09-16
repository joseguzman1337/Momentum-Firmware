"""
Model Context Protocol (MCP) Server for Flipper Zero Emulator v2.
Exposes full emulator control, screen streaming, storage management, Sub-GHz, NFC,
and serial CLI over JSON-RPC 2.0 stdio transport conforming to MCP 2024-11-05 spec.
"""

import sys
import json
import logging
from typing import Dict, Any, List, Optional
from ..emulator import FlipperZeroEmulator
from ..models import ButtonKey, InputType

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s", stream=sys.stderr)
logger = logging.getLogger("flipper-mcp-server")

class FlipperMCPServer:
    """
    Standard Model Context Protocol (MCP) Server for Flipper Zero Emulator.
    """
    def __init__(self, emulator: Optional[FlipperZeroEmulator] = None):
        self.emu = emulator or FlipperZeroEmulator()
        self.tools = self._define_tools()
        self.resources = self._define_resources()
        self.prompts = self._define_prompts()

    def _define_tools(self) -> List[Dict[str, Any]]:
        return [
            {
                "name": "flipper_info",
                "description": "Get Flipper Zero device information, hardware revisions, and firmware metadata.",
                "inputSchema": {
                    "type": "object",
                    "properties": {},
                }
            },
            {
                "name": "flipper_power",
                "description": "Inspect battery status, charger IC state, or reboot the Flipper Zero emulator.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "action": {
                            "type": "string",
                            "enum": ["status", "reboot", "set_charge"],
                            "description": "Action to perform: 'status', 'reboot', or 'set_charge'"
                        },
                        "charge_percent": {
                            "type": "integer",
                            "description": "Optional charge percentage (0-100) when action is 'set_charge'"
                        }
                    },
                    "required": ["action"]
                }
            },
            {
                "name": "flipper_press_button",
                "description": "Send physical button input to the Flipper Zero (UP, DOWN, LEFT, RIGHT, OK, BACK) with specified press type (SHORT, LONG, PRESS, RELEASE).",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "key": {
                            "type": "string",
                            "enum": ["UP", "DOWN", "LEFT", "RIGHT", "OK", "BACK"],
                            "description": "Button key to press"
                        },
                        "type": {
                            "type": "string",
                            "enum": ["SHORT", "LONG", "PRESS", "RELEASE", "REPEAT"],
                            "description": "Press type",
                            "default": "SHORT"
                        }
                    },
                    "required": ["key"]
                }
            },
            {
                "name": "flipper_get_screen",
                "description": "Capture the current 128x64 ST7567 LCD display buffer as an ASCII representation, raw hex, or Base64 PBM image.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "format": {
                            "type": "string",
                            "enum": ["ascii", "base64_pbm", "raw_hex"],
                            "description": "Format for screen buffer capture",
                            "default": "ascii"
                        }
                    }
                }
            },
            {
                "name": "flipper_cli_exec",
                "description": "Execute a command in the Flipper Zero serial CLI (e.g. 'device_info', 'date', 'ps', 'free', 'power info', 'subghz tx', 'nfc read', 'storage list /ext').",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "command": {
                            "type": "string",
                            "description": "CLI command line string to run"
                        }
                    },
                    "required": ["command"]
                }
            },
            {
                "name": "flipper_storage_list",
                "description": "List files and directories in virtual storage (/ext for MicroSD or /int for internal flash).",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "path": {
                            "type": "string",
                            "description": "Directory path to list, e.g. '/ext', '/ext/subghz', '/int'",
                            "default": "/ext"
                        }
                    }
                }
            },
            {
                "name": "flipper_storage_read",
                "description": "Read the contents of a file from Flipper Zero storage (/ext or /int).",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "path": {
                            "type": "string",
                            "description": "Path to the file to read"
                        }
                    },
                    "required": ["path"]
                }
            },
            {
                "name": "flipper_storage_write",
                "description": "Write text or binary data to a file in Flipper Zero storage.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "path": {
                            "type": "string",
                            "description": "Path to write to"
                        },
                        "content": {
                            "type": "string",
                            "description": "Text content to write"
                        }
                    },
                    "required": ["path", "content"]
                }
            },
            {
                "name": "flipper_storage_delete",
                "description": "Delete a file or folder from Flipper Zero storage.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "path": {
                            "type": "string",
                            "description": "Path to delete"
                        }
                    },
                    "required": ["path"]
                }
            },
            {
                "name": "flipper_subghz_tx",
                "description": "Transmit a Sub-GHz RF signal using TI CC1101 transceiver emulation.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "frequency_hz": {
                            "type": "integer",
                            "description": "Frequency in Hz (e.g. 433920000, 315000000, 868350000)",
                            "default": 433920000
                        },
                        "protocol": {
                            "type": "string",
                            "description": "Protocol name (e.g. 'Princeton', 'RAW', 'Nice FLO', 'CAME')",
                            "default": "Princeton"
                        },
                        "key": {
                            "type": "string",
                            "description": "Hex key to transmit",
                            "default": "A1B2C3"
                        },
                        "bit_length": {
                            "type": "integer",
                            "default": 24
                        }
                    }
                }
            },
            {
                "name": "flipper_subghz_rx",
                "description": "Listen for and receive Sub-GHz packets on a given frequency.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "frequency_hz": {
                            "type": "integer",
                            "default": 433920000
                        }
                    }
                }
            },
            {
                "name": "flipper_nfc_read",
                "description": "Scan and read a virtual NFC tag (Mifare Classic, NTAG215, etc.).",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "card_type": {
                            "type": "string",
                            "default": "Mifare Classic"
                        },
                        "uid": {
                            "type": "string",
                            "default": "04 A1 B2 C3 D4 E5 F6"
                        }
                    }
                }
            },
            {
                "name": "flipper_nfc_emulate",
                "description": "Emulate an NFC card with specified UID and parameters.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "uid": {
                            "type": "string",
                            "description": "UID to emulate, e.g. '04 A1 B2 C3 D4 E5 F6'"
                        },
                        "card_type": {
                            "type": "string",
                            "default": "Mifare Classic"
                        }
                    },
                    "required": ["uid"]
                }
            },
            {
                "name": "flipper_rfid_read",
                "description": "Read a 125 kHz LF-RFID tag (EM4100 or HIDProx).",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "protocol": {
                            "type": "string",
                            "default": "EM4100"
                        },
                        "data": {
                            "type": "string",
                            "default": "01 02 03 04 05"
                        }
                    }
                }
            },
            {
                "name": "flipper_sound_and_vibro",
                "description": "Trigger the TIM16 PWM buzzer synthesizer or the vibration motor.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "tone_hz": {
                            "type": "number",
                            "description": "Frequency in Hz to play on buzzer"
                        },
                        "duration_ms": {
                            "type": "integer",
                            "default": 100
                        },
                        "vibro": {
                            "type": "boolean",
                            "description": "Turn vibration motor on (true) or off (false)"
                        }
                    }
                }
            },
            {
                "name": "flipper_run_diagnostics",
                "description": "Execute comprehensive emulator self-diagnostics, peripheral checks, and hardware assertions.",
                "inputSchema": {
                    "type": "object",
                    "properties": {}
                }
            }
        ]

    def _define_resources(self) -> List[Dict[str, Any]]:
        return [
            {
                "uri": "flipper://screen/current",
                "name": "Current Screen Framebuffer",
                "description": "ASCII rendering of the ST7567 128x64 display buffer.",
                "mimeType": "text/plain"
            },
            {
                "uri": "flipper://device/info",
                "name": "Device Information",
                "description": "Device hardware specifications and Flipper Zero OTP profile.",
                "mimeType": "application/json"
            },
            {
                "uri": "flipper://storage/manifest",
                "name": "Storage Manifest",
                "description": "Index of files on /int and /ext.",
                "mimeType": "application/json"
            }
        ]

    def _define_prompts(self) -> List[Dict[str, Any]]:
        return [
            {
                "name": "flipper-audit",
                "description": "Step-by-step security auditing workflow using the Flipper Zero emulator.",
                "arguments": [
                    {"name": "protocol", "description": "Target protocol: subghz, nfc, rfid, or badusb", "required": True}
                ]
            }
        ]

    def handle_request(self, req: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        method = req.get("method")
        msg_id = req.get("id")

        if method == "initialize":
            return {
                "jsonrpc": "2.0",
                "id": msg_id,
                "result": {
                    "protocolVersion": "2024-11-05",
                    "serverInfo": {
                        "name": "flipper-zero-emulator-mcp",
                        "version": "2.0.0"
                    },
                    "capabilities": {
                        "tools": {},
                        "resources": {},
                        "prompts": {}
                    }
                }
            }
        elif method == "notifications/initialized":
            return None
        elif method == "ping":
            return {"jsonrpc": "2.0", "id": msg_id, "result": {}}
        elif method == "tools/list":
            return {
                "jsonrpc": "2.0",
                "id": msg_id,
                "result": {"tools": self.tools}
            }
        elif method == "tools/call":
            params = req.get("params", {})
            tool_name = params.get("name")
            arguments = params.get("arguments", {})
            try:
                res_text = self._call_tool(tool_name, arguments)
                return {
                    "jsonrpc": "2.0",
                    "id": msg_id,
                    "result": {
                        "content": [
                            {"type": "text", "text": res_text}
                        ]
                    }
                }
            except Exception as e:
                return {
                    "jsonrpc": "2.0",
                    "id": msg_id,
                    "result": {
                        "content": [
                            {"type": "text", "text": f"Error executing tool '{tool_name}': {str(e)}"}
                        ],
                        "isError": True
                    }
                }
        elif method == "resources/list":
            return {
                "jsonrpc": "2.0",
                "id": msg_id,
                "result": {"resources": self.resources}
            }
        elif method == "resources/read":
            params = req.get("params", {})
            uri = params.get("uri")
            content = self._read_resource(uri)
            return {
                "jsonrpc": "2.0",
                "id": msg_id,
                "result": {
                    "contents": [
                        {"uri": uri, "mimeType": "text/plain", "text": content}
                    ]
                }
            }
        elif method == "prompts/list":
            return {
                "jsonrpc": "2.0",
                "id": msg_id,
                "result": {"prompts": self.prompts}
            }
        elif method == "prompts/get":
            params = req.get("params", {})
            name = params.get("name")
            args = params.get("arguments", {})
            return {
                "jsonrpc": "2.0",
                "id": msg_id,
                "result": {
                    "description": f"Flipper Zero audit workflow for {args.get('protocol', 'general')}",
                    "messages": [
                        {
                            "role": "user",
                            "content": {
                                "type": "text",
                                "text": f"Guide me through analyzing and testing {args.get('protocol')} using the Flipper Zero emulator tools."
                            }
                        }
                    ]
                }
            }
        else:
            return {
                "jsonrpc": "2.0",
                "id": msg_id,
                "error": {"code": -32601, "message": f"Method not found: {method}"}
            }

    def _call_tool(self, name: str, args: Dict[str, Any]) -> str:
        if name == "flipper_info":
            d = self.emu.get_state_summary()
            return json.dumps(d, indent=2)
            
        elif name == "flipper_power":
            action = args.get("action", "status")
            if action == "status":
                return json.dumps(self.emu.power.get_power_info(), indent=2)
            elif action == "reboot":
                self.emu.reset()
                return "Flipper Zero rebooted successfully."
            elif action == "set_charge":
                pct = int(args.get("charge_percent", 100))
                self.emu.power.set_charge(pct)
                return f"Battery charge set to {pct}% ({self.emu.power.voltage_v:.2f}V)."
            return f"Unknown power action: {action}"

        elif name == "flipper_press_button":
            key = args.get("key", "OK")
            press_type = args.get("type", "SHORT")
            evt = self.emu.press_button(key, press_type)
            screen_txt = self.emu.get_screen_ascii()
            return f"Button {evt.key.value} ({evt.type.value}) processed.\nScreen after input:\n{screen_txt}"

        elif name == "flipper_get_screen":
            fmt = args.get("format", "ascii")
            if fmt == "base64_pbm":
                return self.emu.get_screen_base64_pbm()
            elif fmt == "raw_hex":
                return self.emu.display.get_framebuffer().hex()
            else:
                return self.emu.get_screen_ascii()

        elif name == "flipper_cli_exec":
            cmd = args.get("command", "")
            return self.emu.run_cli_command(cmd)

        elif name == "flipper_storage_list":
            path = args.get("path", "/ext")
            return self.emu.run_cli_command(f"storage list {path}")

        elif name == "flipper_storage_read":
            path = args.get("path", "")
            return self.emu.run_cli_command(f"storage read {path}")

        elif name == "flipper_storage_write":
            path = args.get("path", "")
            content = args.get("content", "")
            if path.startswith("/int"):
                self.emu.flash_mgr.write_file(path, content.encode("utf-8"))
            else:
                self.emu.sd_card.write_file(path, content.encode("utf-8"))
            return f"Successfully written {len(content)} bytes to {path}"

        elif name == "flipper_storage_delete":
            path = args.get("path", "")
            return self.emu.run_cli_command(f"storage remove {path}")

        elif name == "flipper_subghz_tx":
            freq = args.get("frequency_hz", 433920000)
            proto = args.get("protocol", "Princeton")
            key = args.get("key", "A1B2C3")
            bit = args.get("bit_length", 24)
            self.emu.cc1101.set_frequency(freq)
            res = self.emu.cc1101.transmit(proto, key, bit)
            return json.dumps(res, indent=2)

        elif name == "flipper_subghz_rx":
            freq = args.get("frequency_hz", 433920000)
            self.emu.cc1101.set_frequency(freq)
            pkt = self.emu.cc1101.receive_packet("Princeton", "A1B2C3", freq)
            return json.dumps(pkt, indent=2)

        elif name == "flipper_nfc_read":
            card_type = args.get("card_type", "Mifare Classic")
            uid = args.get("uid", "04 A1 B2 C3 D4 E5 F6")
            res = self.emu.nfc_rfid.read_nfc(card_type, uid)
            return json.dumps(res, indent=2)

        elif name == "flipper_nfc_emulate":
            uid = args.get("uid", "04 A1 B2 C3 D4 E5 F6")
            card_type = args.get("card_type", "Mifare Classic")
            self.emu.nfc_rfid.emulate_nfc(uid, card_type)
            return f"Emulating NFC card {card_type} (UID: {uid})"

        elif name == "flipper_rfid_read":
            proto = args.get("protocol", "EM4100")
            data = args.get("data", "01 02 03 04 05")
            res = self.emu.nfc_rfid.read_rfid(proto, data)
            return json.dumps(res, indent=2)

        elif name == "flipper_sound_and_vibro":
            res = []
            if "tone_hz" in args:
                self.emu.audio_vibro.play_tone(args["tone_hz"], args.get("duration_ms", 100))
                res.append(f"Playing {args['tone_hz']} Hz tone")
            if "vibro" in args:
                self.emu.audio_vibro.set_vibro(bool(args["vibro"]))
                res.append(f"Vibro set to {args['vibro']}")
            return ", ".join(res) if res else "No sound/vibro action specified"

        elif name == "flipper_run_diagnostics":
            from ..runner import FlipperEmulatorRunner
            runner = FlipperEmulatorRunner(self.emu)
            report = runner.run_all_tests()
            return json.dumps(report, indent=2)

        raise ValueError(f"Unknown tool: {name}")

    def _read_resource(self, uri: str) -> str:
        if uri == "flipper://screen/current":
            return self.emu.get_screen_ascii()
        elif uri == "flipper://device/info":
            return json.dumps(self.emu.get_state_summary(), indent=2)
        elif uri == "flipper://storage/manifest":
            ext_files = self.emu.sd_card.list_dir("/ext")
            int_files = self.emu.flash_mgr.list_files()
            return json.dumps({"int": int_files, "ext": ext_files}, indent=2)
        return f"Resource not found: {uri}"

    def run_stdio(self):
        logger.info("Flipper Zero Emulator MCP Server started on stdio.")
        while True:
            try:
                line = sys.stdin.readline()
                if not line:
                    break
                line = line.strip()
                if not line:
                    continue
                req = json.loads(line)
                resp = self.handle_request(req)
                if resp is not None:
                    sys.stdout.write(json.dumps(resp) + "\n")
                    sys.stdout.flush()
            except json.JSONDecodeError:
                continue
            except Exception as e:
                logger.error(f"Error handling MCP request: {e}")
                err_resp = {
                    "jsonrpc": "2.0",
                    "id": None,
                    "error": {"code": -32603, "message": str(e)}
                }
                sys.stdout.write(json.dumps(err_resp) + "\n")
                sys.stdout.flush()
