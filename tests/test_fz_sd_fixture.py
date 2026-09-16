import importlib.util
import io
import tarfile
from pathlib import Path

MODULE_PATH = Path(__file__).parents[1] / "scripts" / "fz_sd_fixture.py"
SPEC = importlib.util.spec_from_file_location("fz_sd_fixture", MODULE_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader
SPEC.loader.exec_module(MODULE)


def test_allowlist_rejects_private_paths():
    assert MODULE.allowed_path("/ext/apps/Tools/demo.fap")
    assert not MODULE.allowed_path("/ext/apps_data/demo/config.txt")
    assert not MODULE.allowed_path("/ext/apps/../apps_data/key.txt")
    assert not MODULE.allowed_path("/ext/asset_packs/foo/secret-key.bin")


def test_snapshot_is_deduplicated(tmp_path):
    class Storage:
        def walk(self, root):
            if root == "/ext/apps":
                yield root, [], ["a.fap", "b.fap"]

        def size(self, _path):
            return 4

        def read_file(self, _path):
            return b"same"

    records = MODULE.snapshot_storage(Storage(), tmp_path)
    assert len(records) == 2
    assert records[0]["sha256"] == records[1]["sha256"]
    assert len(list((tmp_path / "blobs").iterdir())) == 1


def test_update_tar_blocks_traversal_and_sensitive_names(tmp_path):
    archive = tmp_path / "resources.tar.gz"
    with tarfile.open(archive, "w:gz") as bundle:
        for name, data in (
            ("safe/icon.bm", b"ok"),
            ("../escape", b"bad"),
            ("keys/private", b"bad"),
            ("example.nfc", b"UID: 04 85 92 8A A0 61 81\n"),
            ("Manifest", b"D:apps_data\n"),
        ):
            info = tarfile.TarInfo(name)
            info.size = len(data)
            bundle.addfile(info, io.BytesIO(data))
    records = MODULE.add_update_resources(tmp_path / "out", archive)
    paths = {item["path"] for item in records}
    assert "update_resources/extracted/safe/icon.bm" in paths
    assert not any(
        value in path for path in paths for value in ("escape", "private", "example.nfc", "Manifest")
    )
