import base64
from pathlib import Path
import sys

import pytest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from fbt_tools.fbt_resources import _blank_png, _fim_text, _normalize_png, _read_api_version


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


def _png_with_chunk(kind, payload):
    png = _blank_png()
    iend = png.rfind(b"\x00\x00\x00\x00IEND")
    from fbt_tools.fbt_resources import _png_chunk

    return png[:iend] + _png_chunk(kind, payload) + png[iend:] + b"trailing-junk"


def test_normalize_png_removes_metadata_and_trailing_bytes():
    source = _png_with_chunk(b"iTXt", b"metadata" * 1000)
    normalized = _normalize_png(source)

    assert normalized == _blank_png()
    assert b"iTXt" not in normalized
    assert normalized.endswith(b"IEND\xaeB`\x82")


def test_normalize_png_rejects_wrong_dimensions():
    with pytest.raises(Exception, match="must be 10x10"):
        _normalize_png(_blank_png(11, 10))


@pytest.mark.parametrize(
    ("kind", "message"),
    ((b"IHDR", "duplicate"), (b"PLTE", "invalid PLTE"), (b"tRNS", "invalid tRNS")),
)
def test_normalize_png_rejects_render_chunks_after_image_data(kind, message):
    source = _png_with_chunk(kind, b"" if kind != b"IHDR" else b"\x00" * 13)
    with pytest.raises(Exception, match=message):
        _normalize_png(source)


def test_normalize_png_rejects_invalid_checksum():
    source = bytearray(_blank_png())
    source[-1] ^= 1
    with pytest.raises(Exception, match="checksum"):
        _normalize_png(bytes(source))


def test_normalize_png_rejects_truncated_png():
    with pytest.raises(Exception, match="incomplete|truncated"):
        _normalize_png(_blank_png()[:-5])


def test_storage_read_response_is_zeroed_and_released_on_short_read():
    source = (ROOT / "applications/services/rpc/rpc_storage.c").read_text(encoding="utf-8")
    function = source[source.index("static void rpc_system_storage_read_process") :]
    function = function[: function.index("static void rpc_system_storage_write_process")]
    allocation = function.index("PB_Main* response = malloc(sizeof(PB_Main));")
    initialization = function.index("*response = (PB_Main)PB_Main_init_zero;")
    open_file = function.index("storage_file_open")
    release = function.index("pb_release(&PB_Main_msg, response);")
    assert allocation < initialization < open_file < release
    assert "if(!fs_operation_success) {\n        pb_release(&PB_Main_msg, response);" in function


def test_api_version_is_read_after_csv_header(tmp_path):
    api = tmp_path / "api_symbols.csv"
    api.write_text("entry,status,name,type,params\nVersion,+,87.6,,\n", encoding="utf-8")
    assert _read_api_version(api) == "87.6"


def test_placeholder_icon_is_a_valid_png_container():
    icon = _blank_png()
    assert icon.startswith(b"\x89PNG\r\n\x1a\n")
    assert b"IHDR" in icon and b"IDAT" in icon
    assert icon.endswith(b"IEND\xaeB`\x82")
