#!/usr/bin/env python3
"""
Test runner script for Flipper Zero Emulator v2.
"""

import sys
import os

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from tools.flipper_emulator.runner import FlipperEmulatorRunner

def main():
    print("==================================================")
    print("  Running Flipper Zero Emulator v2 Test Suite     ")
    print("==================================================")
    runner = FlipperEmulatorRunner()
    report = runner.run_all_tests()
    
    print(f"\nExecution Summary:")
    print(f"  Total tests : {report['total_tests']}")
    print(f"  Passed      : {report['passed']}")
    print(f"  Failed      : {report['failed']}")
    print(f"  Pass Rate   : {report['pass_rate']}")
    print(f"  Duration    : {report['elapsed_ms']} ms")
    print(f"  State Hash  : {report['test_run_hash']}")
    print("\nDetailed Test Log:")
    for t in report["tests"]:
        status_icon = "✓" if t["status"] == "PASS" else "✗"
        print(f"  [{status_icon}] {t['test_name']:<30} : {t['details']} ({t['duration_ms']} ms)")

    sys.exit(0 if report["failed"] == 0 else 1)

if __name__ == "__main__":
    main()
