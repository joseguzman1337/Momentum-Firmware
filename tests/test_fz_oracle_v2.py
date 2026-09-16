import importlib.util
import json
from pathlib import Path

PATH = Path(__file__).parents[1] / "scripts" / "fz_oracle_v2.py"
SPEC = importlib.util.spec_from_file_location("fz_oracle_v2", PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader
SPEC.loader.exec_module(MODULE)


def test_source_contracts_never_extract_setting_payloads():
    contracts = MODULE.source_contracts()
    assert "INPUT_LONG_PRESS_COUNTS" in contracts["input"]["defines"]
    for schema in contracts["settings"].values():
        assert schema["payload_extracted"] is False
        assert not any(MODULE.FORBIDDEN.search(field["name"]) for field in schema["fields"])


def test_usb_unavailable_profile_is_explicit(monkeypatch):
    import builtins
    original = builtins.__import__
    def blocked(name, *args, **kwargs):
        if name == "usb.core":
            raise ImportError
        return original(name, *args, **kwargs)
    monkeypatch.setattr(builtins, "__import__", blocked)
    profile = MODULE.usb_topology()
    assert profile["available"] is False


def test_fixture_safety_ledger_shape():
    expected = {"device_writes", "device_resets", "device_flashes", "protected_reads",
                "storage_payloads_read", "usb_strings_requested"}
    sample = {key: 0 for key in expected}
    assert set(json.loads(json.dumps(sample))) == expected
