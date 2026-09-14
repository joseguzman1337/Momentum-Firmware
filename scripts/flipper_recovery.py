#!/usr/bin/env python3
"""Safe, dependency-light Flipper Zero build, flash, and recovery automation."""

from __future__ import annotations

import argparse
import glob
import hashlib
import json
import os
import signal
import re
import struct
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from typing import Callable, Sequence

CPU2_BOUNDARY = 0x080D7000
FLASH_BASE = 0x08000000
FLASH_PHYSICAL_END = 0x08100000
CONFIRM = "FLASH_VERIFIED_IMAGE"
Runner = Callable[..., subprocess.CompletedProcess]


def workspace() -> Path:
    override = os.environ.get("FLIPPER_RECOVERY_WORKSPACE")
    return Path(override).expanduser().resolve() if override else Path(__file__).resolve().parents[1]


def recovery_dir(root: Path, *, create: bool = False) -> Path:
    path = root / ".recovery"
    if create:
        path.mkdir(mode=0o700, parents=True, exist_ok=True)
    return path


def atomic_json(path: Path, value: dict) -> None:
    path.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as stream:
            json.dump(value, stream, sort_keys=True)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)


def image_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def elf_flash_end(path: Path) -> int:
    """Return highest byte after a PT_LOAD flash payload (including .data LMA)."""
    data = path.read_bytes()
    if len(data) < 52 or data[:4] != b"\x7fELF":
        raise ValueError("not an ELF file")
    elf_class, encoding = data[4], data[5]
    if elf_class not in (1, 2) or encoding not in (1, 2):
        raise ValueError("unsupported ELF class or encoding")
    endian = "<" if encoding == 1 else ">"
    if elf_class == 1:
        header = struct.unpack_from(endian + "16sHHIIIIIHHHHHH", data, 0)
        phoff, phentsize, phnum = header[5], header[9], header[10]
        fmt, need = endian + "IIIIIIII", 32
    else:
        header = struct.unpack_from(endian + "16sHHIQQQIHHHHHH", data, 0)
        phoff, phentsize, phnum = header[5], header[9], header[10]
        fmt, need = endian + "IIQQQQQQ", 56
    if phentsize < need or phoff + phentsize * phnum > len(data):
        raise ValueError("truncated ELF program headers")
    ends: list[int] = []
    for index in range(phnum):
        fields = struct.unpack_from(fmt, data, phoff + index * phentsize)
        if elf_class == 1:
            p_type, _off, _vaddr, paddr, filesz = fields[:5]
        else:
            p_type, _flags, _off, _vaddr, paddr, filesz = fields[:6]
        if p_type == 1 and filesz and FLASH_BASE <= paddr < FLASH_PHYSICAL_END:
            end = paddr + filesz
            if paddr >= CPU2_BOUNDARY or end > CPU2_BOUNDARY:
                raise ValueError(
                    f"unsafe ELF PT_LOAD: 0x{paddr:08X}-0x{end:08X} overlaps or starts "
                    f"at/beyond CPU2 boundary 0x{CPU2_BOUNDARY:08X}"
                )
            ends.append(end)
    if not ends:
        raise ValueError("ELF has no loadable internal-flash payload")
    return max(ends)


def validate_image(path: Path) -> dict:
    path = path.expanduser().resolve()
    if not path.is_file():
        raise ValueError(f"image does not exist: {path}")
    end = elf_flash_end(path)
    if end > CPU2_BOUNDARY:
        raise ValueError(
            f"unsafe ELF: flash payload ends at 0x{end:08X}, beyond CPU2 boundary "
            f"0x{CPU2_BOUNDARY:08X}"
        )
    return {
        "safe": True,
        "image": str(path),
        "sha256": image_sha256(path),
        "flash_end": f"0x{end:08X}",
        "cpu2_boundary": f"0x{CPU2_BOUNDARY:08X}",
        "headroom": CPU2_BOUNDARY - end,
    }


def run_argv(argv: Sequence[str], *, root: Path, timeout: int, runner: Runner = subprocess.run, dry_run: bool = False) -> dict:
    command = [str(item) for item in argv]
    if dry_run:
        return {"ok": True, "dry_run": True, "command": command}
    result = runner(command, cwd=root, capture_output=True, text=True, timeout=timeout, check=False)
    return {
        "ok": result.returncode == 0,
        "command": command,
        "returncode": result.returncode,
        "stdout": result.stdout[-12000:],
        "stderr": result.stderr[-12000:],
    }


def build(*, root: Path, runner: Runner = subprocess.run, dry_run: bool = False) -> dict:
    result = run_argv([root / "fbt", "build/f7-firmware-C/firmware.elf", "SKIP_EXTERNAL=1"], root=root, timeout=1800, runner=runner, dry_run=dry_run)
    if result["ok"] and not dry_run:
        result["validation"] = validate_image(root / "build/f7-firmware-C/firmware.elf")
    return result


def _confirmed(confirm: str) -> None:
    if confirm != CONFIRM:
        raise PermissionError(f"refusing flash: pass confirm={CONFIRM!r}")


def flash_usb(image: Path, *, root: Path, confirm: str, runner: Runner = subprocess.run, dry_run: bool = False) -> dict:
    _confirmed(confirm)
    checked = validate_image(image)
    result = run_argv([root / "fbt", "flash_usb", f"FIRMWARE_ELF={checked['image']}"], root=root, timeout=300, runner=runner, dry_run=dry_run)
    result["validation"] = checked
    return result


def flash_swd(image: Path, *, root: Path, port: str, confirm: str, runner: Runner = subprocess.run, dry_run: bool = False) -> dict:
    _confirmed(confirm)
    checked = validate_image(image)
    gdb = root / "toolchain/current/bin/arm-none-eabi-gdb"
    argv = [gdb, "--batch", checked["image"], "-ex", f"target extended-remote {port}", "-ex", "monitor swdp_scan", "-ex", "attach 1", "-ex", "load", "-ex", "monitor reset", "-ex", "detach"]
    result = run_argv(argv, root=root, timeout=300, runner=runner, dry_run=dry_run)
    result["validation"] = checked
    return result


def devices() -> dict:
    found = []
    try:
        from serial.tools import list_ports  # type: ignore
        for port in list_ports.comports():
            vid, pid = port.vid, port.pid
            kind = "blackmagic_devboard" if (vid, pid) == (0x303A, 0x4001) else "flipper" if (vid, pid) == (0x0483, 0x5740) else "other"
            found.append({"device": port.device, "description": port.description, "vid": vid, "pid": pid, "kind": kind})
        source = "pyserial"
    except ImportError:
        ports = sorted(glob.glob("/dev/cu.usbmodem*"))
        usb = _macos_usb_inventory()
        blackmagic_present = any(d["vid"] == 0x303A and d["pid"] == 0x4001 for d in usb)
        flipper_present = any(d["vid"] == 0x0483 and d["pid"] == 0x5740 for d in usb)
        # Black Magic exposes GDB then UART interfaces; their macOS callout names
        # conventionally end in 1 and 3. Deterministic sorting keeps this safe.
        blackmagic_ports = [p for p in ports if blackmagic_present and not (flipper_present and "flip" in Path(p).name.lower())]
        gdb_port = next((p for p in blackmagic_ports if p[-1:].isdigit() and int(p[-1]) % 2 == 1 and p.endswith("1")), blackmagic_ports[0] if blackmagic_ports else None)
        for port in ports:
            if flipper_present and "flip" in Path(port).name.lower():
                kind, vid, pid = "flipper", 0x0483, 0x5740
            elif port == gdb_port:
                kind, vid, pid = "blackmagic_devboard", 0x303A, 0x4001
            elif blackmagic_present:
                kind, vid, pid = "blackmagic_uart", 0x303A, 0x4001
            elif flipper_present and not blackmagic_present:
                kind, vid, pid = "flipper", 0x0483, 0x5740
            else:
                kind, vid, pid = "unknown", None, None
            found.append({"device": port, "kind": kind, "vid": vid, "pid": pid})
        source = "ioreg_glob_fallback"
    return {"source": source, "devices": found, "blackmagic": [d for d in found if d["kind"] == "blackmagic_devboard"], "flipper": [d for d in found if d["kind"] == "flipper"]}


def verify_good_state() -> dict:
    """Strictly readonly proof that the Flipper itself enumerates over USB CDC."""
    inventory = devices()
    cdc = [d for d in inventory["flipper"] if d.get("vid") == 0x0483 and d.get("pid") == 0x5740]
    evidence = []
    for item in cdc:
        evidence.append(sanitized_evidence(json.dumps({k: item.get(k) for k in ("device", "description", "product", "serial_number") if item.get(k)}, sort_keys=True), 1000))
    return {"good_state": bool(cdc), "criteria": "Flipper USB CDC VID:PID 0483:5740", "flipper_cdc": cdc, "evidence": evidence, "devices": inventory}


def _macos_usb_inventory() -> list[dict]:
    try:
        result = subprocess.run(["ioreg", "-r", "-c", "IOUSBHostDevice", "-l", "-w0"], capture_output=True, text=True, timeout=8, check=False)
    except (OSError, subprocess.SubprocessError):
        return []
    devices_found = []
    # ioreg trees contain nested services, so first recognize the authoritative
    # device signatures across the full tree rather than relying on indentation.
    signatures = ((0x303A, 0x4001, "Blackmagic ESP32"), (0x0483, 0x5740, "Flipper Zero"))
    for vid, pid, product in signatures:
        if re.search(rf'"idVendor"\s*=\s*{vid}\b', result.stdout) and re.search(rf'"idProduct"\s*=\s*{pid}\b', result.stdout):
            devices_found.append({"vid": vid, "pid": pid, "product": product})
    for block in re.split(r"(?=^[+|` ]*o )", result.stdout, flags=re.MULTILINE):
        vendor = re.search(r'"idVendor"\s*=\s*(\d+)', block)
        product_id = re.search(r'"idProduct"\s*=\s*(\d+)', block)
        if not (vendor and product_id):
            continue
        product = re.search(r'"USB Product Name"\s*=\s*"([^"]*)"', block) or re.search(r'"kUSBProductString"\s*=\s*"([^"]*)"', block)
        item = {"vid": int(vendor.group(1)), "pid": int(product_id.group(1)), "product": product.group(1) if product else ""}
        if not any(d["vid"] == item["vid"] and d["pid"] == item["pid"] for d in devices_found): devices_found.append(item)
    return devices_found


def _external_watchers() -> list[str]:
    try:
        listing = subprocess.run(["ps", "-axo", "pid=,ppid=,comm=,args="], capture_output=True, text=True, timeout=5, check=False)
    except (OSError, subprocess.SubprocessError):
        return []
    rows = []
    for line in listing.stdout.splitlines():
        parts = line.strip().split(None, 3)
        if len(parts) < 4 or not parts[0].isdigit() or not parts[1].isdigit():
            continue
        rows.append((int(parts[0]), int(parts[1]), parts[2], parts[3]))
    ancestors = {os.getpid()}; parent_map = {pid: ppid for pid, ppid, _comm, _args in rows}
    cursor = os.getpid()
    while cursor in parent_map and parent_map[cursor] not in ancestors:
        cursor = parent_map[cursor]; ancestors.add(cursor)
    matches = []
    for pid, _ppid, comm, args in rows:
        if pid in ancestors:
            continue
        executable = Path(comm).name.lower()
        tokens = args.split()
        invoked = Path(tokens[0]).name.lower() if tokens else executable
        script = Path(tokens[1]).name.lower() if len(tokens) > 1 and invoked.startswith("python") else ""
        if executable == "qflipper-cli" or invoked == "qflipper-cli" or script.startswith("auto_flash_devboard") or invoked.startswith("auto_flash_devboard"):
            matches.append(f"{pid} {comm} {args}")
    return matches


def monitor_paths(root: Path, *, create: bool = False) -> dict[str, Path]:
    base = recovery_dir(root, create=create)
    return {name: base / filename for name, filename in {"pid": "monitor.pid", "state": "monitor.json", "arm": "armed.json", "log": "monitor.log", "history": "history.jsonl"}.items()}


def _read_json(path: Path) -> dict | None:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        return None


def _pid_alive(pid: int) -> bool:
    try:
        os.kill(pid, 0)
        return True
    except (OSError, ValueError):
        return False


def _pid_is_our_worker(pid: int) -> bool:
    if not _pid_alive(pid):
        return False
    try:
        result = subprocess.run(["ps", "-p", str(pid), "-o", "command="], capture_output=True, text=True, timeout=5, check=False)
    except (OSError, subprocess.SubprocessError):
        return False
    command = result.stdout.strip()
    return str(Path(__file__).resolve()) in command and "__monitor-worker" in command


def monitor_status(root: Path) -> dict:
    paths = monitor_paths(root)
    try:
        pid = int(paths["pid"].read_text().strip())
    except (FileNotFoundError, ValueError, OSError):
        pid = None
    running = bool(pid and _pid_is_our_worker(pid))
    external = _external_watchers()
    return {"running": running, "pid": pid if running else None, "external_watchers": external, "state": _read_json(paths["state"]), "armed": _read_json(paths["arm"]), "log": str(paths["log"])}


def monitor_observation(root: Path) -> dict:
    """Strictly read-only observation used by readonly MCP tools."""
    return {"devices": devices(), "monitor": monitor_status(root)}


def sanitized_evidence(value: str, limit: int = 2000) -> str:
    value = re.sub(r"(?i)(token|password|secret|authorization|api[_-]?key)\s*[:=]\s*\S+", r"\1=[REDACTED]", value)
    return value if len(value) <= limit else value[:limit] + "...[truncated]"


def monitor_backoff(consecutive_errors: int, base: float = 1.0, maximum: float = 30.0) -> float:
    return min(maximum, base * (2 ** min(max(consecutive_errors, 0), 16)))


def append_history(path: Path, record: dict) -> None:
    path.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    payload = (json.dumps(record, sort_keys=True, separators=(",", ":")) + "\n").encode()
    fd = os.open(path, os.O_WRONLY | os.O_APPEND | os.O_CREAT, 0o600)
    try:
        os.write(fd, payload); os.fsync(fd)
    finally:
        os.close(fd)


def get_monitor_history(root: Path, limit: int = 100, since: float | None = None, state: str | None = None) -> list[dict]:
    """Read JSONL history without creating or modifying any file."""
    path = monitor_paths(root)["history"]
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except FileNotFoundError:
        return []
    records = []
    for line in lines:
        try: record = json.loads(line)
        except json.JSONDecodeError: continue
        if since is not None and record.get("timestamp", 0) < since: continue
        if state is not None and record.get("state") != state: continue
        records.append(record)
    return records[-max(0, min(limit, 1000)):]


def get_monitor_debug_summary(root: Path) -> dict:
    history = get_monitor_history(root, limit=1000)
    current = monitor_status(root)
    return {"current": current, "record_count": len(history), "last_record": history[-1] if history else None, "recent_transitions": [r for r in history if r.get("event") == "transition"][-10:]}


def arm_monitor(image: Path, *, root: Path, port: str, confirm: str) -> dict:
    _confirmed(confirm)
    checked = validate_image(image)
    value = {"image": checked["image"], "sha256": checked["sha256"], "port": port, "armed_at": time.time(), "attempts": 0, "last_error": None, "next_retry_at": 0}
    atomic_json(monitor_paths(root, create=True)["arm"], value)
    return {"armed": True, **value}


def monitor_once(root: Path, *, runner: Runner = subprocess.run, dry_run: bool = False, heartbeat_seconds: float = 60.0, absent_threshold: int = 3) -> dict:
    paths = monitor_paths(root, create=True)
    started = time.monotonic(); previous = _read_json(paths["state"]) or {}; now = time.time()
    observed = devices()
    result: dict = {"observed_at": now, "devices": observed, "action": "observe_only"}
    armed = _read_json(paths["arm"])
    if armed and observed["blackmagic"]:
        image = Path(armed.get("image", ""))
        if now < float(armed.get("next_retry_at", 0)):
            result["action"] = "retry_wait"
            result["next_retry_at"] = armed["next_retry_at"]
        else:
            try:
                checked = validate_image(image)
                if checked["sha256"] != armed.get("sha256"):
                    raise ValueError("armed image hash changed")
                result["action"] = "swd_flash"
                result["flash"] = flash_swd(image, root=root, port=armed["port"], confirm=CONFIRM, runner=runner, dry_run=dry_run)
                flash_output = "\n".join((result["flash"].get("stdout", ""), result["flash"].get("stderr", "")))
                positive_load = bool(re.search(r"(?i)(loading section|transfer rate|bytes written)", flash_output))
                negative_load = bool(re.search(r"(?i)(load (failed|error)|error while loading|failed to load)", flash_output))
                verified_load = result["flash"].get("returncode") == 0 and positive_load and not negative_load
                result["verified_load"] = verified_load
                if verified_load:
                    paths["arm"].unlink(missing_ok=True)
                else:
                    raise RuntimeError(f"SWD load not verified (rc={result['flash'].get('returncode')})\n{flash_output}")
            except Exception as error:
                attempts = int(armed.get("attempts", 0)) + 1
                last_error = sanitized_evidence(str(error), 2000)
                next_retry_at = now + monitor_backoff(attempts, base=2.0, maximum=300.0)
                armed.update({"attempts": attempts, "last_error": last_error, "next_retry_at": next_retry_at, "last_attempt_at": now})
                atomic_json(paths["arm"], armed)
                result["action"] = "flash_failed" if "flash" in result else "refused"
                result["error"] = last_error
                result["next_retry_at"] = next_retry_at
    if result["action"] == "swd_flash": candidate_state = "flash_succeeded"
    elif result["action"] == "flash_failed": candidate_state = "flash_failed"
    elif result["action"] == "refused": candidate_state = "refused"
    elif result["action"] == "retry_wait": candidate_state = previous.get("state") or "retry_wait"
    elif observed["flipper"]: candidate_state = "flipper_online"
    elif observed["blackmagic"]: candidate_state = "devboard_online"
    elif armed: candidate_state = "armed_waiting"
    else: candidate_state = "absent"
    threshold = max(3, int(absent_threshold))
    raw_absent = candidate_state == "absent"
    miss_count = int(previous.get("miss_count", 0)) + 1 if raw_absent else 0
    # Backward migration: pre-hysteresis state persisted the effective inventory
    # only in `devices`. Preserve it across the first transient miss after upgrade.
    last_known_devices = previous.get("last_known_devices") or previous.get("devices") or {}
    if not raw_absent:
        last_known_devices = observed
    transient_miss = raw_absent and miss_count < threshold
    if transient_miss:
        state = previous.get("state") or "unknown"
        result["raw_devices"] = observed
        result["devices"] = last_known_devices
    else:
        state = candidate_state
    failed = state in ("flash_failed", "refused")
    errors = int(previous.get("consecutive_errors", 0)) + 1 if failed else 0
    cycle = int(previous.get("cycle", 0)) + 1
    transition = state != previous.get("state")
    last_heartbeat = float(previous.get("last_heartbeat", 0))
    event = "transient_miss" if transient_miss else "transition" if transition else "heartbeat" if now - last_heartbeat >= heartbeat_seconds else None
    flash = result.get("flash", {})
    evidence = sanitized_evidence("\n".join(filter(None, [flash.get("stdout", ""), flash.get("stderr", "")])))
    record = {"timestamp": now, "cycle": cycle, "event": event, "state": state, "previous_state": previous.get("state"), "probe_port": (armed or {}).get("port"), "swd_outcome": result["action"], "target": (armed or {}).get("image"), "image_sha256": (armed or {}).get("sha256"), "consecutive_errors": errors, "miss_count": miss_count, "raw_source": observed.get("source"), "elapsed_seconds": round(time.monotonic() - started, 6), "gdb_rc": flash.get("returncode"), "evidence": evidence}
    if event:
        append_history(paths["history"], record); last_heartbeat = now
    result.update({"state": state, "effective_state": state, "cycle": cycle, "transition": transition, "transient_miss": transient_miss, "miss_count": miss_count, "absent_threshold": threshold, "last_known_devices": last_known_devices, "consecutive_errors": errors, "last_heartbeat": last_heartbeat, "next_delay": monitor_backoff(errors)})
    atomic_json(paths["state"], result)
    return result


def recover_to_good_state(image: Path, *, root: Path, port: str, confirm: str, build_first: bool = True, runner: Runner = subprocess.run, dry_run: bool = False) -> dict:
    """Confirmed, resumable recovery state-machine; completion requires real CDC."""
    _confirmed(confirm)
    before = verify_good_state()
    if before["good_state"]:
        return {"complete": True, "action": "already_good", "verification": before}
    build_result = None
    if build_first:
        build_result = build(root=root, runner=runner, dry_run=dry_run)
        if not build_result.get("ok"):
            return {"complete": False, "action": "build_failed", "build": build_result, "verification": before}
        if not dry_run:
            image = root / "build/f7-firmware-C/firmware.elf"
    checked = validate_image(image)
    status = monitor_status(root)
    existing_arm = status.get("armed")
    if existing_arm and existing_arm.get("sha256") != checked["sha256"]:
        return {"complete": False, "action": "different_image_already_armed", "validation": checked, "armed": existing_arm, "verification": before}
    prior = [record for record in get_monitor_history(root, limit=1000) if record.get("state") == "flash_succeeded" and record.get("image_sha256") == checked["sha256"]]
    if prior and not status.get("armed"):
        return {"complete": False, "action": "awaiting_good_state", "duplicate_flash_prevented": True, "validation": checked, "last_success": prior[-1], "verification": before}
    if dry_run:
        return {"complete": False, "action": "dry_run", "validation": checked, "build": build_result, "verification": before}
    if not status.get("armed"):
        arm_monitor(image, root=root, port=port, confirm=confirm)
    cycle = monitor_once(root, runner=runner)
    monitor = monitor_start(root)
    after = verify_good_state()
    return {"complete": after["good_state"], "action": "good_state_verified" if after["good_state"] else "awaiting_good_state", "validation": checked, "build": build_result, "cycle": cycle, "monitor": monitor, "verification": after}


def monitor_start(root: Path, *, interval: float = 3.0) -> dict:
    status = monitor_status(root)
    if status["running"]:
        return {"started": False, "reason": "already_running", **status}
    if status["external_watchers"]:
        return {"started": False, "reason": "external_watcher_detected", **status}
    paths = monitor_paths(root, create=True)
    try:
        claim_fd = os.open(paths["pid"], os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    except FileExistsError:
        # Never remove an empty claim: another starter may be between claim and spawn.
        try:
            recorded = paths["pid"].read_text().strip()
        except OSError:
            recorded = ""
        if not recorded:
            return {"started": False, "reason": "singleton_claimed"}
        try:
            recorded_pid = int(recorded)
        except ValueError:
            return {"started": False, "reason": "invalid_pid_record"}
        if _pid_is_our_worker(recorded_pid):
            return {"started": False, "reason": "already_running", **monitor_status(root)}
        paths["pid"].unlink(missing_ok=True)
        return monitor_start(root, interval=interval)
    log = paths["log"].open("ab", buffering=0)
    try:
        process = subprocess.Popen([sys.executable, str(Path(__file__).resolve()), "__monitor-worker", "--interval", str(max(interval, 0.5))], cwd=root, stdin=subprocess.DEVNULL, stdout=log, stderr=log, start_new_session=True)
        os.write(claim_fd, f"{process.pid}\n".encode())
        os.fsync(claim_fd)
    except Exception:
        paths["pid"].unlink(missing_ok=True)
        raise
    finally:
        os.close(claim_fd)
        log.close()
    return {"started": True, "pid": process.pid, "log": str(paths["log"])}


def monitor_stop(root: Path) -> dict:
    paths = monitor_paths(root)
    status = monitor_status(root)
    if not status["running"]:
        paths["pid"].unlink(missing_ok=True)
        return {"stopped": False, "reason": "stale_or_not_running", "signaled": False}
    os.kill(status["pid"], signal.SIGTERM)
    for _ in range(30):
        if not _pid_alive(status["pid"]):
            break
        time.sleep(0.1)
    paths["pid"].unlink(missing_ok=True)
    return {"stopped": True, "pid": status["pid"]}


def monitor_worker(root: Path, interval: float) -> int:
    running = True
    def stop(_signum, _frame):
        nonlocal running
        running = False
    signal.signal(signal.SIGTERM, stop)
    signal.signal(signal.SIGINT, stop)
    while running:
        try:
            result = monitor_once(root)
            if result.get("transition"):
                print(json.dumps(result), flush=True)
            delay = max(interval, float(result.get("next_delay", interval)))
        except Exception as error:
            print(json.dumps({"error": sanitized_evidence(str(error)), "observed_at": time.time()}), flush=True)
            delay = monitor_backoff(1, base=max(interval, 0.5))
        time.sleep(max(delay, 0.5))
    return 0


def parser() -> argparse.ArgumentParser:
    cli = argparse.ArgumentParser(description=__doc__)
    sub = cli.add_subparsers(dest="command", required=True)
    sub.add_parser("status")
    check = sub.add_parser("validate"); check.add_argument("image", type=Path)
    build_cmd = sub.add_parser("build"); build_cmd.add_argument("--dry-run", action="store_true")
    for name in ("flash-usb", "flash-swd"):
        cmd = sub.add_parser(name); cmd.add_argument("image", type=Path); cmd.add_argument("--confirm", default=""); cmd.add_argument("--dry-run", action="store_true")
        if name == "flash-swd": cmd.add_argument("--port", default="/dev/cu.usbmodem1101")
    arm = sub.add_parser("monitor-arm"); arm.add_argument("image", type=Path); arm.add_argument("--port", default="/dev/cu.usbmodem1101"); arm.add_argument("--confirm", default="")
    once = sub.add_parser("monitor-once"); once.add_argument("--dry-run", action="store_true")
    start = sub.add_parser("monitor-start"); start.add_argument("--interval", type=float, default=3.0)
    sub.add_parser("monitor-stop"); sub.add_parser("monitor-status")
    worker = sub.add_parser("__monitor-worker"); worker.add_argument("--interval", type=float, default=3.0)
    return cli


def main(argv: Sequence[str] | None = None) -> int:
    args = parser().parse_args(argv); root = workspace()
    try:
        if args.command == "status": value = {"workspace": str(root), **devices(), "monitor": monitor_status(root)}
        elif args.command == "validate": value = validate_image(args.image)
        elif args.command == "build": value = build(root=root, dry_run=args.dry_run)
        elif args.command == "flash-usb": value = flash_usb(args.image, root=root, confirm=args.confirm, dry_run=args.dry_run)
        elif args.command == "flash-swd": value = flash_swd(args.image, root=root, port=args.port, confirm=args.confirm, dry_run=args.dry_run)
        elif args.command == "monitor-arm": value = arm_monitor(args.image, root=root, port=args.port, confirm=args.confirm)
        elif args.command == "monitor-once": value = monitor_once(root, dry_run=args.dry_run)
        elif args.command == "monitor-start": value = monitor_start(root, interval=args.interval)
        elif args.command == "monitor-stop": value = monitor_stop(root)
        elif args.command == "monitor-status": value = monitor_status(root)
        else: return monitor_worker(root, args.interval)
        print(json.dumps(value, indent=2, sort_keys=True)); return 0 if value.get("ok", True) else 1
    except Exception as error:
        print(json.dumps({"ok": False, "error": str(error)}, sort_keys=True)); return 2


if __name__ == "__main__":
    raise SystemExit(main())
