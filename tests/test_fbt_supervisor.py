import sys
from pathlib import Path

from scripts.fbt_supervisor import (
    FailureKind,
    classify_line,
    extract_selfupdate_manifest,
    next_usb_chunk_size,
    selfupdate_retry_command,
    select_failure,
    supervise,
)


REPOSITORY = Path(__file__).resolve().parents[1]


def test_classifies_usb_timeout_as_safe_transient():
    assert (
        classify_line("TimeoutError: Timed out waiting for '>: '")
        is FailureKind.USB_TRANSIENT
    )


def test_classifies_compiler_error_as_non_retryable():
    assert classify_line("source.c:42:7: error: undeclared identifier") is FailureKind.BUILD


def test_specific_usb_cause_beats_generic_scons_error_wrapper():
    kinds = {
        classify_line("Storage error: file/dir not exist"),
        classify_line("********** FBT ERRORS **********"),
    }

    assert select_failure(kinds) is FailureKind.USB_TRANSIENT


def test_usb_autoremediation_reduces_chunk_size_to_safe_floor():
    assert next_usb_chunk_size(4096) == 2048
    assert next_usb_chunk_size(2048) == 1024
    assert next_usb_chunk_size(1024) == 1024


def test_usb_retry_reuses_built_manifest_without_reentering_scons(tmp_path):
    manifest = tmp_path / "update.fuf"
    manifest.write_text("Filetype: Flipper firmware upgrade configuration\n")
    line = f"  Local manifest: {manifest}"

    extracted = extract_selfupdate_manifest(line)
    command = selfupdate_retry_command(extracted, port="/dev/ttyACM0")

    assert extracted == manifest
    assert command[-3:] == ["-p", "/dev/ttyACM0", str(manifest)]
    assert command[1].endswith("scripts/selfupdate.py")


def test_retries_transient_failure_and_preserves_timestamped_logs(tmp_path):
    counter = tmp_path / "counter"
    command = [
        sys.executable,
        "-c",
        (
            "from pathlib import Path; import sys; "
            f"p=Path({str(counter)!r}); n=int(p.read_text())+1 if p.exists() else 1; "
            "p.write_text(str(n)); "
            "print(\"TimeoutError: Timed out waiting for '>: '\") if n == 1 else print('ok'); "
            "sys.exit(1 if n == 1 else 0)"
        ),
    ]

    result = supervise(
        command,
        phase="transfer",
        log_dir=tmp_path / "logs",
        max_attempts=2,
        remediation=lambda _kind, _attempt: True,
        retry_delay=0,
    )

    assert result == 0
    assert counter.read_text() == "2"
    log_text = "".join(path.read_text() for path in (tmp_path / "logs").glob("*.log"))
    assert "[transfer][attempt=1]" in log_text
    assert "[transfer][attempt=2]" in log_text
    assert "TimeoutError" in log_text


def test_fbt_routes_preflight_and_build_through_supervisor():
    entrypoint = (REPOSITORY / "fbt").read_text()

    assert entrypoint.count("scripts/fbt_supervisor.py") == 2
    assert '--phase preflight' in entrypoint
    assert '--phase build' in entrypoint
