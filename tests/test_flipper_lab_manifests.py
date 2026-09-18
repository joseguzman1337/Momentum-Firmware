import base64
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from fbt_tools.fbt_resources import _blank_png, _fim_text, _read_api_version


def test_fim_contains_every_field_required_by_flipper_lab():
    icon = _blank_png()
    text = _fim_text(
        name="Demo",
        icon=icon,
        api="87.6",
        uid="nx-local-demo",
        version_uid="nx-local-sha256",
        path="/ext/apps/Tools/demo.fap",
    )
    expected = {
        "Filetype": "Flipper Application Installation Manifest",
        "Version": "1",
        "Full Name": "Demo",
        "Icon": base64.b64encode(icon).decode("ascii"),
        "Version Build API": "87.6",
        "UID": "nx-local-demo",
        "Version UID": "nx-local-sha256",
        "Path": "/ext/apps/Tools/demo.fap",
    }
    assert dict(line.split(": ", 1) for line in text.splitlines()) == expected


def test_fim_rejects_empty_required_values():
    try:
        _fim_text(name="", icon=b"\x00", api="87.6", uid="id", version_uid="v", path="/ext/a.fap")
    except Exception as error:
        assert "Incomplete" in str(error)
    else:
        raise AssertionError("empty manifest values must be rejected")


def test_fim_rejects_empty_icon():
    try:
        _fim_text(name="Demo", icon=b"", api="87.6", uid="id", version_uid="v", path="/ext/a.fap")
    except Exception as error:
        assert "no icon" in str(error)
    else:
        raise AssertionError("an empty icon must be rejected")


def test_api_version_is_read_after_csv_header(tmp_path):
    api = tmp_path / "api_symbols.csv"
    api.write_text("entry,status,name,type,params\nVersion,+,87.6,,\n", encoding="utf-8")
    assert _read_api_version(api) == "87.6"


def test_placeholder_icon_is_a_valid_png_container():
    icon = _blank_png()
    assert icon.startswith(b"\x89PNG\r\n\x1a\n")
    assert b"IHDR" in icon and b"IDAT" in icon
    assert icon.endswith(b"IEND\xaeB`\x82")
