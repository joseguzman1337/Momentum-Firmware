from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
VERSION_SOURCE = ROOT / "lib/toolbox/version.c"


def test_firmware_provenance_comes_from_the_current_build():
    source = VERSION_SOURCE.read_text()

    assert ".git_hash = GIT_COMMIT," in source
    assert ".git_branch = GIT_BRANCH," in source
    assert ".build_date = BUILD_DATE," in source
    assert ".target = TARGET," in source
    assert ".build_is_dirty = BUILD_DIRTY," in source
    assert ".firmware_origin = FIRMWARE_ORIGIN," in source
    assert ".git_origin = GIT_ORIGIN," in source
    assert '"e1784e74"' not in source
