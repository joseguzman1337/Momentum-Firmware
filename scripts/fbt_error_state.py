#!/usr/bin/env python3
"""Persistent, fail-closed error state for FBT builds."""

from __future__ import annotations

import argparse
import os
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable


class BuildErrorState:
    def __init__(self, repository: Path | str) -> None:
        self.root = Path(repository) / ".fbt-state"
        self.pending_error = self.root / "pending-errors.log"
        self.preflight_error = self.root / "preflight-errors.log"
        self.archive_dir = self.root / "archive"

    @staticmethod
    def _atomic_write(path: Path, lines: Iterable[str]) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        temporary = path.with_suffix(path.suffix + ".tmp")
        text = "\n".join(str(line).rstrip("\n") for line in lines) + "\n"
        temporary.write_text(text, encoding="utf-8")
        os.replace(temporary, path)

    def record_failure(self, failures: Iterable[str], phase: str = "build") -> None:
        target = self.preflight_error if phase == "preflight" else self.pending_error
        self._atomic_write(target, failures)

    def record_success(self, phase: str = "build") -> None:
        target = self.preflight_error if phase == "preflight" else self.pending_error
        target.unlink(missing_ok=True)

    def check_pending(self, acknowledged: bool) -> bool:
        if not self.pending_error.exists():
            return True
        if not acknowledged:
            return False
        self.archive_dir.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S.%fZ")
        shutil.move(self.pending_error, self.archive_dir / f"{timestamp}.log")
        return True


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=("check",))
    parser.add_argument("--repository", default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    state = BuildErrorState(args.repository)
    acknowledged = os.environ.get("FBT_ACK_PREVIOUS_ERRORS") == "1"
    if state.check_pending(acknowledged):
        return 0
    print("FBT blocked: unresolved errors from the previous build:", file=sys.stderr)
    print(state.pending_error.read_text(encoding="utf-8"), file=sys.stderr, end="")
    print(
        "Review/fix them, then acknowledge with FBT_ACK_PREVIOUS_ERRORS=1.",
        file=sys.stderr,
    )
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
