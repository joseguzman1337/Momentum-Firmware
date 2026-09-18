import json
import base64
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from scripts import bundle_marketplace_resources as bundler
from scripts.fbt_tools.fbt_resources import _blank_png


APP_ID = "0123456789abcdef01234567"
VERSION_ID = "89abcdef0123456701234567"


def report(complete=True):
    return {
        "complete": complete,
        "verified_apps": 1 if complete else 0,
        "catalog_apps": 1,
        "api": "87.6",
        "apps": [
            {
                "alias": "current",
                "application_id": APP_ID,
                "version_id": VERSION_ID,
                "name": "Current App",
                "icon": base64.b64encode(_blank_png()).decode(),
                "path": "Tools/current.fap",
            }
        ],
    }


class MarketplaceResourceBundleTest(unittest.TestCase):
    def test_preserves_resources_and_replaces_apps_with_complete_stage(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            base = root / "base"
            apps = root / "apps"
            destination = root / "result"
            (base / "dolphin").mkdir(parents=True)
            (base / "Manifest").write_text("V:0\nT:123\n")
            (base / "dolphin" / "state.bin").write_bytes(b"resource")
            (base / "apps" / "Old").mkdir(parents=True)
            (base / "apps" / "Old" / "old.fap").write_bytes(b"old")
            (base / "apps_manifests").mkdir()
            (base / "apps_manifests" / "old.fim").write_text("UID: nx-local-old\n")
            (apps / "Tools").mkdir(parents=True)
            (apps / "Tools" / "current.fap").write_bytes(b"current")
            (apps / "marketplace-lock.json").write_text(
                json.dumps(report())
            )

            with mock.patch("subprocess.run") as run:
                bundler.bundle(base, apps, destination, Path("assets.py"), 123)

            self.assertEqual((destination / "dolphin" / "state.bin").read_bytes(), b"resource")
            self.assertEqual((destination / "apps" / "Tools" / "current.fap").read_bytes(), b"current")
            self.assertFalse((destination / "apps" / "Old" / "old.fap").exists())
            manifests = list((destination / "apps_manifests").glob("*.fim"))
            self.assertEqual([item.name for item in manifests], ["current.fim"])
            manifest = manifests[0].read_text()
            self.assertIn(f"UID: {APP_ID}", manifest)
            self.assertIn(f"Version UID: {VERSION_ID}", manifest)
            self.assertNotIn("nx-local", manifest)
            run.assert_called_once()

    def test_rejects_incomplete_stage_without_replacing_destination(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            base = root / "base"
            apps = root / "apps"
            destination = root / "result"
            base.mkdir()
            (base / "Manifest").write_text("V:0\nT:123\n")
            apps.mkdir()
            destination.mkdir()
            (destination / "preserved").write_text("yes")
            (apps / "marketplace-lock.json").write_text(
                json.dumps(report(False))
            )

            with self.assertRaisesRegex(RuntimeError, "incomplete"):
                bundler.bundle(base, apps, destination, Path("assets.py"), 123)
            self.assertEqual((destination / "preserved").read_text(), "yes")

    def test_rejects_non_catalog_identity_without_replacing_destination(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            base = root / "base"
            apps = root / "apps"
            destination = root / "result"
            (base / "apps").mkdir(parents=True)
            (base / "Manifest").write_text("V:0\nT:123\n")
            (apps / "Tools").mkdir(parents=True)
            (apps / "Tools/current.fap").write_bytes(b"current")
            invalid = report()
            invalid["apps"][0]["application_id"] = "nx-local-current"
            (apps / "marketplace-lock.json").write_text(json.dumps(invalid))
            destination.mkdir()
            (destination / "preserved").write_text("yes")

            with self.assertRaisesRegex(RuntimeError, "application ID"):
                bundler.bundle(base, apps, destination, Path("assets.py"), 123)
            self.assertEqual((destination / "preserved").read_text(), "yes")


if __name__ == "__main__":
    unittest.main()
