#!/usr/bin/env python3
"""Reproducible front-end for the workspace Flipper emulation backends."""

from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
LOGS = ROOT / ".ai" / "logs" / "qemu-fw"
CAPABILITIES = Path(__file__).with_name("capabilities.json")


def _run(command: list[str]) -> int:
    return subprocess.run(command, cwd=ROOT, check=False).returncode


def main() -> int:
    parser = argparse.ArgumentParser(description="Run and compare Flipper Zero emulation backends")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("capabilities")
    run = sub.add_parser("run")
    run.add_argument("--backend", choices=("native", "renode"), default="native")
    run.add_argument("--log", type=Path)
    run.add_argument("--instructions", type=int, default=20_000_000)
    verify = sub.add_parser("verify")
    verify.add_argument("--instructions", type=int, default=20_000_000)

    args = parser.parse_args()
    if args.command == "capabilities":
        print(json.dumps(json.loads(CAPABILITIES.read_text()), indent=2))
        return 0

    LOGS.mkdir(parents=True, exist_ok=True)
    if args.command == "run":
        log = args.log or LOGS / f"unified-{args.backend}.log"
        if args.backend == "native":
            return _run([str(LOGS / "run_fap_studio_engine.sh"), str(log), str(args.instructions)])
        return _run([str(LOGS / "run_renode_elf.sh"), str(log)])

    native = _run([
        str(LOGS / "run_fap_studio_engine.sh"),
        str(LOGS / "unified-native.log"),
        str(args.instructions),
    ])
    renode = _run([str(LOGS / "run_renode_elf.sh"), str(LOGS / "unified-renode.log")])
    report = {"native": native, "renode": renode, "passed": native == 0 and renode == 0}
    (LOGS / "unified-verification.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
