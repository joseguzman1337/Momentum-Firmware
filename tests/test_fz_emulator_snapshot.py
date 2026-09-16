import importlib.util
import json
from pathlib import Path


MODULE_PATH = Path(__file__).parents[1] / "scripts" / "fz_emulator_snapshot.py"
SPEC = importlib.util.spec_from_file_location("fz_emulator_snapshot", MODULE_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader
SPEC.loader.exec_module(MODULE)


def test_sanitize_removes_device_identifiers():
    raw = "hardware_uid : DEADBEEF\r\nhardware_model : Flipper Zero\r\nradio_ble_mac : AABBCC\r\n>: "
    clean = MODULE.sanitize(raw)
    assert "DEADBEEF" not in clean
    assert "AABBCC" not in clean
    assert "hardware_model : Flipper Zero" in clean
    assert clean.count("<redacted>") == 2


def test_transport_rejects_mutating_commands_without_opening_device():
    transport = object.__new__(MODULE.SerialTransport)
    try:
        transport.command("storage remove /int/.bt.settings")
    except ValueError as error:
        assert "read-only allow-list" in str(error)
    else:
        raise AssertionError("mutating command was accepted")


def test_capture_records_no_device_mutations(tmp_path, monkeypatch):
    class FakeTransport:
        def command(self, command):
            return command + "\r\nhardware_uid: 1234\r\nhardware_model: Flipper Zero\r\n>: "

        def close(self):
            pass

    monkeypatch.setattr(MODULE, "usb_descriptor_profile", lambda: {"serial": "<redacted>"})
    manifest_path = MODULE.capture(FakeTransport(), tmp_path, [])
    manifest = json.loads(manifest_path.read_text())
    assert manifest["safety"]["device_writes"] == 0
    assert len(manifest["commands"]) == len(MODULE.READ_ONLY_COMMANDS)
    assert "1234" not in (tmp_path / "cli" / "device_info.txt").read_text()


def test_backup_artifact_name_is_redacted():
    name = MODULE.safe_artifact_name(Path("/tmp/MyDevice-backup-20260915.tgz"))
    assert name == "<redacted>.tgz"


def test_minimal_screen_frame_wire_decode():
    # ScreenFrame(data=b"abc", orientation=1)
    fields = MODULE.protobuf_fields(bytes.fromhex("0a036162631001"))
    assert fields == [(1, 2, b"abc"), (2, 0, 1)]


def test_update_metadata_excludes_option_bytes(tmp_path):
    update = tmp_path / "update.fuf"
    update.write_text("Target: 7\nFirmware: firmware.dfu\nOB reference: SECRET\n")
    assert MODULE.parse_update_metadata(update) == {"Target": "7", "Firmware": "firmware.dfu"}
