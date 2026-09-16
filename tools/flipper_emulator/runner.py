#!/usr/bin/env python3
"""Stage and run the native STM32WB55 emulator without touching hardware."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import threading
import time
from pathlib import Path

from tools.flipper_emulator.usb import VirtualCdcService

from tools.flipper_emulator.models import Cpu2Service, PublicC2Firmware, SafeDeviceInfo

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_ENGINE = ROOT / ".tools/flipper-fap-studio/runtime/stm32/source/target/release/stm32-emulator"
DEFAULT_SVD = ROOT / ".ai/logs/qemu-fw/fap-studio-profile/STM32WB55_CM4.svd"
EVENT_RE = re.compile(r"FLIPPER_(INPUT|FRAME|AUDIO)\s+(.*)$")
CLK_RE = re.compile(r"\[clk=(\d+) pc=0x([0-9a-fA-F]+)\]")

MODELED = {
    "cpu": "Cortex-M4 instructions, exceptions, NVIC, SysTick and DWT",
    "memory": "flash aliases, SRAM1, SRAM2, SRAM2 alias and factory OTP window",
    "clock_power": "RCC and RTC compatibility behavior; not cycle accurate",
    "gpio_input": "GPIO, EXTI and BUTTON <name> PRESS|RELEASE control protocol",
    "display": "ST7567 over SPI2, emitted as FLIPPER_FRAME events",
    "storage": "SPI2 SD image with 512-byte block read/write and DMA",
    "serial": "USART probe",
    "audio": "TIM16 PWM decoded as FLIPPER_AUDIO events",
}
REPLAY_STUBS = {
    "cpu2_fus_radio": "sanitized version/status replay only; no M0+ or radio execution"
}
UNMODELED = ["CPU2 execution", "radio/BLE protocol", "NFC", "infrared output", "raw /int persistence", "electrical GPIO", "exact timing"]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_spec(path: Path) -> dict:
    data = json.loads(path.read_text())
    required = {"firmware", "output"}
    missing = required - data.keys()
    if missing:
        raise ValueError(f"missing required keys: {', '.join(sorted(missing))}")
    if not isinstance(data.get("max_instructions", 20_000_000), int):
        raise ValueError("max_instructions must be an integer")
    for event in data.get("inputs", []):
        if event.get("action") not in {"PRESS", "RELEASE"} or not event.get("button"):
            raise ValueError("each input needs button and PRESS or RELEASE action")
    return data


def validate_oracle_snapshot(path: Path) -> dict:
    """Validate a sanitized, read-only snapshot without opening hardware."""
    manifest = json.loads((path / "manifest.json").read_text())
    errors = []
    if manifest.get("schema") != 1:
        errors.append("unsupported snapshot schema")
    safety = manifest.get("safety", {})
    for counter in ("device_flashes", "device_resets", "device_writes"):
        if safety.get(counter) != 0:
            errors.append(f"unsafe snapshot counter: {counter}")
    if safety.get("identifiers_redacted") is not True:
        errors.append("snapshot identifiers are not declared redacted")
    fixtures = sorted((path / "cli").glob("*.txt"))
    declared = {item.get("sha256") for item in manifest.get("commands", [])}
    observed = {sha256(item) for item in fixtures}
    if declared != observed:
        errors.append("snapshot fixture hashes differ from manifest")
    identifier = re.compile(r"\b(?:[0-9A-Fa-f]{12}|[0-9A-Fa-f]{16}|[0-9A-Fa-f]{24})\b")
    if any(identifier.search(item.read_text(errors="replace")) for item in fixtures):
        errors.append("snapshot may contain an unredacted identifier")
    screen = manifest.get("screen", {})
    screen_sha256 = None
    if screen.get("captured"):
        screen_path = path / screen.get("file", "")
        if not screen_path.is_file():
            errors.append("declared framebuffer fixture is missing")
        else:
            screen_sha256 = sha256(screen_path)
            if screen_sha256 != screen.get("sha256"):
                errors.append("framebuffer fixture hash differs from manifest")
    return {
        "valid": not errors,
        "errors": errors,
        "manifest_sha256": sha256(path / "manifest.json"),
        "fixture_count": len(fixtures),
        "storage_contents": safety.get("storage_contents_downloaded") is True,
        "screen_capture": manifest.get("screen", {}).get("captured") is True,
        "screen_sha256": screen_sha256,
        "usb_metadata": bool(manifest.get("usb")),
        "radio_replay": sanitized_radio_replay(path),
    }


def sanitized_radio_replay(snapshot: Path) -> dict:
    """Extract non-unique CPU2/FUS/radio version facts for deterministic replay."""
    info_path = snapshot / "cli" / "device_info.txt"
    allowed = {
        "radio_alive", "radio_mode", "radio_fus_major", "radio_fus_minor",
        "radio_fus_sub", "radio_stack_type", "radio_stack_major",
        "radio_stack_minor", "radio_stack_sub", "radio_stack_branch",
        "radio_stack_release",
    }
    replay = {"classification": "oracle-version-replay", "cpu2_execution": False}
    if not info_path.is_file():
        return replay
    for line in info_path.read_text().splitlines():
        if ":" not in line:
            continue
        key, value = (part.strip() for part in line.split(":", 1))
        if key in allowed:
            replay[key] = value
    return replay


def build_platform_models(spec: dict, oracle: dict | None) -> dict:
    """Build deterministic service metadata without opening physical hardware."""
    info = SafeDeviceInfo.from_json(Path(spec["device_info_model"]).expanduser().resolve()) \
        if spec.get("device_info_model") else SafeDeviceInfo()
    replay = (oracle or {}).get("radio_replay", {})
    cpu2 = Cpu2Service(replay)
    cpu2.command("start")
    result = {
        "info_table": {
            "flash_kib": info.flash_kib, "sram_kib": info.sram_kib,
            "package": info.package, "revision": info.revision,
            "option_bytes": info.option_bytes, "writes_allowed": False,
        },
        "hsem": {"semaphores": 32, "ownership": "modeled"},
        "ipcc": {"channels_per_direction": 6, "delivery": "modeled"},
        "cpu2": {"execution": False, "service": cpu2.command("get_state"),
                 "version": cpu2.command("get_version")},
    }
    if spec.get("c2_firmware"):
        result["c2_reference"] = PublicC2Firmware.inspect(
            Path(spec["c2_firmware"]).expanduser().resolve()).__dict__
    return result


def validate_sd_tree(root: Path) -> dict:
    manifest = json.loads((root / "manifest.json").read_text())
    tree = root / "tree"
    errors = []
    total = 0
    for entry in manifest.get("files", []):
        relative = Path(entry.get("path", ""))
        if relative.is_absolute() or ".." in relative.parts:
            errors.append(f"unsafe path: {relative}")
            continue
        path = tree / relative
        if not path.is_file() or path.is_symlink():
            errors.append(f"missing or unsafe fixture: {relative}")
            continue
        total += path.stat().st_size
        if path.stat().st_size != entry.get("size") or sha256(path) != entry.get("sha256"):
            errors.append(f"fixture mismatch: {relative}")
    return {"valid": not errors, "errors": errors, "files": len(manifest.get("files", [])), "bytes": total}


def build_sd_image(source: Path, destination: Path, content_bytes: int) -> None:
    """Create an isolated FAT image from a validated fixture tree on macOS."""
    # The fixture uses content-addressed hard links. hdiutil attempts to
    # preserve those links on FAT and fails with ENOTSUP, so materialize plain
    # files in the already-isolated stage first.
    materialized = destination.parent / "sd-root"
    shutil.copytree(source, materialized, copy_function=shutil.copyfile)
    size_mb = max(64, ((content_bytes + 32 * 1024 * 1024) // (1024 * 1024)) + 1)
    command = [
        "/usr/bin/hdiutil", "create", "-quiet", "-ov", "-size", f"{size_mb}m",
        "-fs", "MS-DOS", "-volname", "FLIPPER", "-srcfolder", str(materialized),
        "-format", "UDRW", str(destination),
    ]
    subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)


def yaml_quote(value: str) -> str:
    return json.dumps(value)


def profile(firmware: str, sd_image: str | None) -> str:
    devices = "  usart_probe:\n    - peripheral: USART1\n"
    if sd_image:
        devices += (
            "  sd_card:\n    - peripheral: SPI2\n"
            f"      file: {yaml_quote(sd_image)}\n      chip_select: PC12\n      card_detect: PC10\n"
        )
    devices += "  st7567:\n    - peripheral: SPI2\n      data_command: PB1\n      chip_select: PC11\n"
    return f"""cpu:
  svd: STM32WB55_CM4.svd
  vector_table: 0x08000000
regions:
  - {{name: FLASH_ALIAS, start: 0x00000000, load: {yaml_quote(firmware)}, size: 0x00100000}}
  - {{name: FLASH, start: 0x08000000, load: {yaml_quote(firmware)}, size: 0x00100000}}
  - {{name: SRAM1, start: 0x20000000, size: 0x00030000}}
  - {{name: SRAM2, start: 0x20030000, size: 0x00010000}}
  - {{name: SRAM2_ALIAS, start: 0x10000000, size: 0x00010000}}
  - {{name: FACTORY_OTP, start: 0x1fff7000, size: 0x00001000}}
peripherals: {{}}
devices:
{devices}framebuffers: []
"""


def parse_trace(raw: str) -> list[dict]:
    events = []
    for line in raw.splitlines():
        marker = EVENT_RE.search(line)
        if not marker:
            continue
        clock = CLK_RE.search(line)
        events.append({
            "sequence": len(events),
            "instruction": int(clock.group(1)) if clock else None,
            "pc": f"0x{int(clock.group(2), 16):08x}" if clock else None,
            "kind": marker.group(1).lower(),
            "payload": marker.group(2),
        })
    return events


def run(spec_path: Path) -> int:
    spec = load_spec(spec_path)
    firmware = Path(spec["firmware"]).expanduser().resolve()
    output = Path(spec["output"]).expanduser().resolve()
    engine = Path(spec.get("engine", DEFAULT_ENGINE)).expanduser().resolve()
    svd = Path(spec.get("svd", DEFAULT_SVD)).expanduser().resolve()
    for label, path in (("firmware", firmware), ("engine", engine), ("svd", svd)):
        if not path.is_file():
            raise FileNotFoundError(f"{label} not found: {path}")
    oracle = None
    if spec.get("oracle_snapshot"):
        oracle_path = Path(spec["oracle_snapshot"]).expanduser().resolve()
        oracle = validate_oracle_snapshot(oracle_path)
        if not oracle["valid"]:
            raise ValueError("invalid oracle snapshot: " + "; ".join(oracle["errors"]))
    sd_fixture = None
    if spec.get("sd_tree"):
        sd_root = Path(spec["sd_tree"]).expanduser().resolve()
        sd_fixture = validate_sd_tree(sd_root)
        if not sd_fixture["valid"]:
            raise ValueError("invalid SD fixture: " + "; ".join(sd_fixture["errors"][:5]))
    platform_models = build_platform_models(spec, oracle)
    output.mkdir(parents=True, exist_ok=True)
    stage = output / "stage"
    if stage.exists():
        shutil.rmtree(stage)
    stage.mkdir()
    shutil.copy2(firmware, stage / "full.bin")
    shutil.copy2(svd, stage / "STM32WB55_CM4.svd")
    sd = spec.get("sd_image")
    if sd:
        shutil.copy2(Path(sd).expanduser().resolve(), stage / "sd-card.img")
    elif sd_fixture:
        build_sd_image(sd_root / "tree", stage / "sd-card.dmg", sd_fixture["bytes"])
    staged_sd = "sd-card.img" if sd else ("sd-card.dmg" if sd_fixture else None)
    (stage / "config.yaml").write_text(profile("full.bin", staged_sd))

    virtual_usb = None
    virtual_usb_path = None
    if spec.get("virtual_usb"):
        flash_image = Path(spec.get("internal_flash_image", output / "internal-flash.json")).expanduser().resolve()
        framebuffer = None
        if spec.get("oracle_snapshot"):
            screen = json.loads((oracle_path / "manifest.json").read_text()).get("screen", {})
            screen_path = oracle_path / screen.get("file", "")
            if screen.get("captured") and screen_path.is_file():
                framebuffer = screen_path.read_bytes()
        virtual_usb = VirtualCdcService(flash_image, framebuffer)
        virtual_usb_path = virtual_usb.start()

    command = [str(engine), "config.yaml", "--color", "never", "--max-instructions", str(spec.get("max_instructions", 20_000_000)), "--dump-stack", "64"]
    for _ in range(int(spec.get("verbosity", 0))):
        command.append("-v")
    started = time.time()
    live_control = bool(spec.get("live_control"))
    control_fifo = output / "control.fifo"
    runtime_status = output / "runtime-status.json"
    if live_control:
        control_fifo.unlink(missing_ok=True)
        os.mkfifo(control_fifo, 0o600)
    proc = subprocess.Popen(command, cwd=stage, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT, text=True, bufsize=1,
                            env={**os.environ, "SDL_VIDEODRIVER": "dummy"})
    assert proc.stdin and proc.stdout
    status = {
        "phase": "running", "pid": proc.pid, "started_at": started,
        "last_event_sequence": None, "control_fifo": str(control_fifo) if live_control else None,
        "virtual_usb_endpoint": virtual_usb_path,
        "internal_flash_image": str(flash_image) if virtual_usb else None,
    }
    runtime_status.write_text(json.dumps(status, sort_keys=True) + "\n")
    for event in spec.get("inputs", []):
        proc.stdin.write(f"BUTTON {event['button']} {event['action']}\n")
    proc.stdin.flush()

    def forward_live_control() -> None:
        while proc.poll() is None and control_fifo.exists():
            try:
                with control_fifo.open() as stream:
                    for raw_command in stream:
                        command_line = raw_command.strip()
                        if not command_line:
                            continue
                        if command_line == "STOP":
                            proc.stdin.close()
                            return
                        if not re.fullmatch(
                            r"BUTTON [A-Za-z0-9_]+ (?:PRESS|RELEASE)", command_line
                        ):
                            continue
                        proc.stdin.write(command_line + "\n")
                        proc.stdin.flush()
            except (BrokenPipeError, OSError, ValueError):
                return

    if live_control:
        threading.Thread(target=forward_live_control, daemon=True).start()
    else:
        proc.stdin.close()

    raw_lines: list[str] = []
    events: list[dict] = []
    with (output / "engine.log").open("w") as raw_stream, (output / "events.jsonl").open("w") as event_stream:
        for line in proc.stdout:
            raw_lines.append(line)
            raw_stream.write(line)
            raw_stream.flush()
            parsed = parse_trace(line)
            if not parsed:
                continue
            event = parsed[0]
            event["sequence"] = len(events)
            events.append(event)
            event_stream.write(json.dumps(event, sort_keys=True) + "\n")
            event_stream.flush()
            status["last_event_sequence"] = event["sequence"]
            runtime_status.write_text(json.dumps(status, sort_keys=True) + "\n")
    proc.stdout.close()
    returncode = proc.wait()
    raw = "".join(raw_lines)
    status.update(
        phase="succeeded" if returncode == 0 else "failed",
        returncode=returncode,
        finished_at=time.time(),
    )
    runtime_status.write_text(json.dumps(status, sort_keys=True) + "\n")
    control_fifo.unlink(missing_ok=True)
    if virtual_usb:
        virtual_usb.close()
    frame_hashes = []
    for event in events:
        if event["kind"] == "frame":
            try:
                frame_hashes.append(hashlib.sha256(bytes.fromhex(event["payload"])).hexdigest())
            except ValueError:
                pass
    framebuffer_match = bool(
        oracle and oracle["screen_sha256"] and oracle["screen_sha256"] in frame_hashes
    )
    stable_tail_frames = 0
    if frame_hashes:
        last = frame_hashes[-1]
        stable_tail_frames = next(
            (index for index, value in enumerate(reversed(frame_hashes), 1) if value != last),
            len(frame_hashes) + 1,
        ) - 1
    report = {
        "schema_version": 1, "returncode": returncode, "elapsed_seconds": round(time.time() - started, 3),
        "command": command, "firmware": {"path": str(firmware), "sha256": sha256(firmware)},
        "engine": {"path": str(engine), "sha256": sha256(engine)}, "event_count": len(events),
        "coverage": {"modeled": MODELED, "replay_stubs": REPLAY_STUBS, "not_modeled": UNMODELED},
        "oracle_snapshot": oracle,
        "platform_models": platform_models,
        "sd_fixture": sd_fixture,
        "virtual_usb": {
            "enabled": virtual_usb is not None,
            "endpoint": virtual_usb_path,
            "transport": "PTY CDC with delimited Flipper protobuf RPC" if virtual_usb else None,
            "persistent_internal_flash": str(flash_image) if virtual_usb else None,
        },
        "live_control": {
            "enabled": live_control,
            "transport": "POSIX FIFO forwarding to native engine stdin" if live_control else None,
            "runtime_status": str(runtime_status),
        },
        "differential": {
            "emulated_frame_count": len(frame_hashes),
            "unique_emulated_frames": len(set(frame_hashes)),
            "captured_framebuffer_match": framebuffer_match,
            "stable_tail_frames": stable_tail_frames,
            "stable_ui_observed": stable_tail_frames >= 5,
        },
        "gaps": [
            gap for gap, present in (
                ("SD directory metadata exists, but no sector image or file contents were staged", oracle is not None and not oracle["storage_contents"] and not sd_fixture),
                ("resource bytes were not captured and cannot be staged into the SD model", oracle is not None and not oracle["storage_contents"] and not sd_fixture),
                ("no framebuffer fixture is available for pixel comparison", oracle is not None and not oracle["screen_capture"]),
                ("USB controller is not MCU-executed; host CDC/RPC is a process-isolated compatibility transport", virtual_usb is not None),
                ("USB is metadata-only; the backend has no functional USB transport", oracle is not None and oracle["usb_metadata"] and virtual_usb is None),
                ("CPU2/FUS/radio are version/status replay only; protocol-accurate execution remains unmodeled", oracle is not None),
                ("internal /int persistence is absent; firmware falls back to default settings", virtual_usb is None),
            ) if present
        ],
        "artifacts": {
            "raw_log": "engine.log", "events": "events.jsonl",
            "runtime_status": "runtime-status.json", "profile": "stage/config.yaml",
        },
    }
    (output / "report.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(json.dumps(report, sort_keys=True))
    return returncode


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("spec", type=Path, help="JSON run specification")
    try:
        return run(parser.parse_args().spec)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"flipper-emulator: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
