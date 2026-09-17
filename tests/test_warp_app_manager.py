import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts import warp_app_manager


class WarpAppManagerPathTest(unittest.TestCase):
    def test_catalog_target_accepts_a_normal_alias(self) -> None:
        with tempfile.TemporaryDirectory() as directory, patch.object(
            warp_app_manager, "USER_APPS_DIR", directory
        ):
            self.assertEqual(
                Path(warp_app_manager.catalog_target("example_app")),
                (Path(directory) / "example_app").resolve(),
            )

    def test_catalog_target_rejects_missing_and_escaping_aliases(self) -> None:
        aliases = (None, "", ".", "..", "../escape", "nested/app", "/absolute", "bad alias")
        with tempfile.TemporaryDirectory() as directory, patch.object(
            warp_app_manager, "USER_APPS_DIR", directory
        ):
            for alias in aliases:
                with self.subTest(alias=alias), self.assertRaises(ValueError):
                    warp_app_manager.catalog_target(alias)

    def test_repository_url_accepts_supported_https_forges(self) -> None:
        urls = (
            "https://github.com/example/app.git",
            "https://gitlab.com/example/app",
            "https://codeberg.org/example/app",
        )
        for url in urls:
            with self.subTest(url=url):
                self.assertEqual(warp_app_manager.validated_repository_url(url), url)

    def test_repository_url_rejects_unsafe_transports_and_authorities(self) -> None:
        urls = (
            None,
            "",
            "--upload-pack=payload",
            "git@github.com:example/app.git",
            "http://github.com/example/app.git",
            "https://user:token@github.com/example/app.git",
            "https://github.com:443/example/app.git",
            "https://evil.example/example/app.git",
            "https://github.com/example/app.git?option=value",
            "https://github.com/only-owner",
            "https://[malformed/example/app",
        )
        for url in urls:
            with self.subTest(url=url), self.assertRaises(ValueError):
                warp_app_manager.validated_repository_url(url)


if __name__ == "__main__":
    unittest.main()
