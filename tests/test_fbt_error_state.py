import os
from pathlib import Path

from scripts.fbt_error_state import BuildErrorState


def test_failed_build_is_persisted_and_blocks_next_build(tmp_path):
    state = BuildErrorState(tmp_path)

    state.record_failure(["foo.c: compiler error"])

    assert state.pending_error.read_text() == "foo.c: compiler error\n"
    assert state.check_pending(acknowledged=False) is False


def test_acknowledging_archives_pending_error(tmp_path):
    state = BuildErrorState(tmp_path)
    state.record_failure(["foo.c: compiler error"])

    assert state.check_pending(acknowledged=True) is True
    assert not state.pending_error.exists()
    assert [path.read_text() for path in state.archive_dir.iterdir()] == [
        "foo.c: compiler error\n"
    ]


def test_success_clears_pending_error(tmp_path):
    state = BuildErrorState(tmp_path)
    state.record_failure(["old error"])

    state.record_success()

    assert not state.pending_error.exists()


def test_preflight_failure_is_recorded_separately(tmp_path):
    state = BuildErrorState(tmp_path)

    state.record_failure(["missing dependency"], phase="preflight")

    assert state.preflight_error.read_text() == "missing dependency\n"
    assert not state.pending_error.exists()
