import hashlib
import base64
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts import official_marketplace_sync as marketplace
from scripts.fbt_tools.fbt_resources import _blank_png


class OfficialMarketplaceSyncTests(unittest.TestCase):
    def app(self, payload=b"\x7fELFtest"):
        return {
            "_id": "0123456789abcdef01234567",
            "alias": "demo",
            "category_id": "cat-id",
            "current_version": {
                "_id": "89abcdef0123456701234567",
                "name": "Demo App",
                "icon_uri": "https://catalog.flipperzero.one/api/v0/application/version/assets/icon",
                "version": "1.2",
                "current_build": {"fap_hash": hashlib.sha256(payload).hexdigest()},
            },
        }

    @staticmethod
    def fetcher(payload):
        return lambda url: _blank_png() if "/assets/" in url else payload

    def test_sync_writes_verified_fap_and_receipt(self):
        payload = b"\x7fELFtest"
        with tempfile.TemporaryDirectory() as directory, patch.object(
            marketplace, "catalog_apps", return_value=[self.app(payload)]
        ), patch.object(marketplace, "category_map", return_value={"cat-id": "Tools"}), patch.object(
            marketplace, "fetch", side_effect=self.fetcher(payload)
        ):
            root = Path(directory)
            report = marketplace.sync(root, target="f7", api="87.6")
            self.assertTrue(report["complete"])
            self.assertEqual((root / "Tools/demo.fap").read_bytes(), payload)
            receipt = report["apps"][0]
            self.assertEqual(receipt["application_id"], "0123456789abcdef01234567")
            self.assertEqual(receipt["version_id"], "89abcdef0123456701234567")
            self.assertEqual(receipt["name"], "Demo App")
            self.assertEqual(base64.b64decode(receipt["icon"]), _blank_png())
            self.assertTrue(json.loads((root / "marketplace-lock.json").read_text())["complete"])

    def test_hash_mismatch_fails_closed(self):
        with tempfile.TemporaryDirectory() as directory, patch.object(
            marketplace, "catalog_apps", return_value=[self.app()]
        ), patch.object(marketplace, "category_map", return_value={"cat-id": "Tools"}), patch.object(
            marketplace, "fetch", return_value=b"\x7fELFtampered"
        ):
            with self.assertRaisesRegex(RuntimeError, "sync incomplete"):
                marketplace.sync(Path(directory), target="f7", api="87.6")
            self.assertFalse((Path(directory) / "Tools/demo.fap").exists())

    def test_non_elf_fails_closed_even_with_matching_hash(self):
        payload = b"not a fap"
        with tempfile.TemporaryDirectory() as directory, patch.object(
            marketplace, "catalog_apps", return_value=[self.app(payload)]
        ), patch.object(marketplace, "category_map", return_value={"cat-id": "Tools"}), patch.object(
            marketplace, "fetch", side_effect=self.fetcher(payload)
        ):
            with self.assertRaisesRegex(RuntimeError, "sync incomplete"):
                marketplace.sync(Path(directory), target="f7", api="87.6")

    def test_unsafe_alias_cannot_escape_stage(self):
        app = self.app()
        app["alias"] = "../../escape"
        with tempfile.TemporaryDirectory() as directory, patch.object(
            marketplace, "catalog_apps", return_value=[app]
        ), patch.object(marketplace, "category_map", return_value={"cat-id": "Tools"}), patch.object(
            marketplace, "fetch", side_effect=self.fetcher(b"\x7fELFtest")
        ):
            with self.assertRaisesRegex(RuntimeError, "sync incomplete"):
                marketplace.sync(Path(directory) / "apps", target="f7", api="87.6")
            self.assertFalse((Path(directory) / "escape.fap").exists())

    def test_failed_refresh_preserves_previous_complete_stage(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "apps"
            (root / "Tools").mkdir(parents=True)
            old = root / "Tools/old.fap"
            old.write_bytes(b"old")
            with patch.object(marketplace, "catalog_apps", return_value=[self.app()]), patch.object(
                marketplace, "category_map", return_value={"cat-id": "Tools"}
            ), patch.object(marketplace, "fetch", side_effect=OSError("network down")):
                with self.assertRaisesRegex(RuntimeError, "demo: network down"):
                    marketplace.sync(root, target="f7", api="87.6")
            self.assertEqual(old.read_bytes(), b"old")

    def test_bundled_apps_are_merged_before_official_overwrite(self):
        payload = b"\x7fELFofficial"
        with tempfile.TemporaryDirectory() as directory, patch.object(
            marketplace, "catalog_apps", return_value=[self.app(payload)]
        ), patch.object(marketplace, "category_map", return_value={"cat-id": "Tools"}), patch.object(
            marketplace, "fetch", side_effect=self.fetcher(payload)
        ):
            base = Path(directory) / "base"
            (base / "Games").mkdir(parents=True)
            (base / "Games/local.fap").write_bytes(b"local")
            destination = Path(directory) / "combined"
            marketplace.sync(destination, target="f7", api="87.6", base=base)
            self.assertEqual((destination / "Games/local.fap").read_bytes(), b"local")
            self.assertEqual((destination / "Tools/demo.fap").read_bytes(), payload)

    def test_empty_catalog_and_duplicate_ids_are_rejected(self):
        with patch.object(marketplace, "fetch_json", return_value=[]):
            with self.assertRaisesRegex(RuntimeError, "no applications"):
                marketplace.catalog_apps()
        duplicate = self.app()
        with patch.object(marketplace, "fetch_json", return_value=[duplicate, duplicate]):
            with self.assertRaisesRegex(RuntimeError, "duplicate application IDs"):
                marketplace.catalog_apps()

    def test_changing_catalog_inventory_fails_before_staging(self):
        changed = self.app()
        changed["_id"] = "changed-id"
        with tempfile.TemporaryDirectory() as directory, patch.object(
            marketplace, "catalog_apps", side_effect=[[self.app()], [changed]]
        ):
            with self.assertRaisesRegex(RuntimeError, "changed during inventory"):
                marketplace.sync(Path(directory) / "apps", target="f7", api="87.6")
            self.assertFalse((Path(directory) / "apps").exists())
