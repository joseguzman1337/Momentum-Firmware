from pathlib import Path
import struct


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "applications/services/desktop/helpers/slideshow.c"
FIRSTBOOT = ROOT / "build/f7-firmware-C/resources/dolphin/firstboot.bin"


def test_firstboot_slideshow_state_and_partial_frames_are_initialized():
    source = SOURCE.read_text()
    assert "memset(ret, 0, sizeof(Slideshow));" in source
    assert "calloc(header.frame_count, sizeof(uint8_t*))" in source
    assert "if(!slideshow) return;" in source
    assert "if(icon->frames)" in source


def test_built_firstboot_slideshow_has_complete_seven_frame_contract():
    data = FIRSTBOOT.read_bytes()
    magic, version, width, height, frame_count = struct.unpack_from("<IBBBB", data)
    assert magic == 0x72676468
    assert version <= 1
    assert (width, height, frame_count) == (128, 64, 7)

    offset = 8
    for _ in range(frame_count):
        (size,) = struct.unpack_from("<H", data, offset)
        assert size > 0
        offset += 2 + size
        assert offset <= len(data)
    assert offset == len(data)
