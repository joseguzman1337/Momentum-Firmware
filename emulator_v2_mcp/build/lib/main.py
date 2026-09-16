#!/usr/bin/env python3
"""
Interactive Launcher and Command-Line Interface for Flipper Zero Emulator v2.
"""

import sys
import os
import argparse

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from tools.flipper_emulator.emulator import FlipperZeroEmulator
from tools.flipper_emulator.models import DEFAULT_PROFILE

def interactive_shell(emu: FlipperZeroEmulator):
    print("==================================================")
    print(f"  Flipper Zero Emulator v2 (Unit: {emu.profile.device_name})")
    print("==================================================")
    print("Type 'help' for Flipper CLI commands, 'screen' to display LCD,")
    print("'btn <KEY>' to press button (UP, DOWN, LEFT, RIGHT, OK, BACK),")
    print("or 'quit' / 'exit' to leave.\n")
    
    while True:
        try:
            line = input("flipper>: ").strip()
            if not line:
                continue
            if line.lower() in ("exit", "quit"):
                print("Exiting emulator. Goodbye!")
                break
            elif line.lower() == "screen":
                print(emu.get_screen_ascii())
            elif line.lower().startswith("btn "):
                parts = line.split()
                key = parts[1].upper()
                ptype = parts[2].upper() if len(parts) > 2 else "SHORT"
                evt = emu.press_button(key, ptype)
                print(f"[*] Button {evt.key.value} ({evt.type.value}) pressed.")
                print(emu.get_screen_ascii())
            else:
                out = emu.run_cli_command(line)
                if out:
                    print(out)
        except (KeyboardInterrupt, EOFError):
            print("\nExiting.")
            break

def main():
    parser = argparse.ArgumentParser(description="Flipper Zero Emulator v2 Runner")
    parser.add_argument("--mcp", action="store_true", help="Start as Model Context Protocol (MCP) server over stdio")
    parser.add_argument("--screen", action="store_true", help="Print current LCD screen and exit")
    parser.add_argument("--device-info", action="store_true", help="Print device info and exit")
    parser.add_argument("--cmd", type=str, help="Execute a single CLI command and exit")
    parser.add_argument("--test", action="store_true", help="Run full diagnostic test suite and exit")
    args = parser.parse_args()

    emu = FlipperZeroEmulator()

    if args.mcp:
        from tools.flipper_emulator.mcp.server import FlipperMCPServer
        server = FlipperMCPServer(emu)
        server.run_stdio()
    elif args.screen:
        print(emu.get_screen_ascii())
    elif args.device_info:
        print(emu.run_cli_command("device_info"))
    elif args.cmd:
        print(emu.run_cli_command(args.cmd))
    elif args.test:
        from tools.flipper_emulator.runner import FlipperEmulatorRunner
        runner = FlipperEmulatorRunner(emu)
        report = runner.run_all_tests()
        print(f"Test Run Results ({report['passed']}/{report['total_tests']} passed - {report['pass_rate']}):")
        for t in report["tests"]:
            print(f"  [{t['status']}] {t['test_name']}: {t['details']}")
    else:
        interactive_shell(emu)

if __name__ == "__main__":
    main()
