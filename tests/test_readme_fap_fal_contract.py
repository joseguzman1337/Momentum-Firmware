import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class ReadmeFapFalContractTest(unittest.TestCase):
    def read(self, relative: str) -> str:
        return (ROOT / relative).read_text(encoding="utf-8")

    def assert_manifest_app(self, relative: str, appid: str, app_type: str) -> None:
        manifest = self.read(relative)
        app_blocks = (f"App({part}" for part in manifest.split("App(")[1:])
        matching_blocks = [block for block in app_blocks if f'appid="{appid}"' in block]
        self.assertEqual(len(matching_blocks), 1, f"expected exactly one App block for {appid}")
        self.assertIn(
            f"apptype=FlipperAppType.{app_type}",
            matching_blocks[0].split("\nApp(", 1)[0],
            f"{appid} must remain {app_type}",
        )

    def test_readme_describes_the_sd_card_delivery_contract(self) -> None:
        readme = self.read("ReadMe.md")
        self.assertIn("FAP/FAL Delivery Matrix", readme)
        self.assertIn("SD-card", readme)
        self.assertNotIn("fully autonomous AI-driven", readme)
        self.assertNotIn("working 24/7", readme)
        self.assertNotIn("bulletproof reliability", readme)
        self.assertEqual(readme.count("```") % 2, 0, "Markdown fences must be balanced")

    def test_promised_apps_are_sd_card_faps(self) -> None:
        faps = (
            ("applications/main/momentum_app/application.fam", "momentum_app", "MENUEXTERNAL"),
            ("applications/main/bad_usb/application.fam", "bad_kb", "MENUEXTERNAL"),
            ("applications/system/findmy/application.fam", "findmy", "EXTERNAL"),
            ("applications/external/ble_spam/application.fam", "ble_spam", "EXTERNAL"),
            ("applications/external/nfc_maker/application.fam", "nfc_maker", "EXTERNAL"),
            ("applications/external/wardriver/application.fam", "wardriver", "EXTERNAL"),
            ("applications/external/esp_flasher/application.fam", "esp_flasher", "EXTERNAL"),
            ("applications/external/usb_ethernet/application.fam", "usb_ethernet", "EXTERNAL"),
            ("applications/external/mass_storage/application.fam", "mass_storage", "EXTERNAL"),
        )
        for path, appid, app_type in faps:
            with self.subTest(appid=appid):
                self.assert_manifest_app(path, appid, app_type)

    def test_promised_extension_families_are_fal_plugins(self) -> None:
        plugins = (
            ("applications/services/cli/application.fam", "cli_free"),
            ("applications/main/nfc/application.fam", "nfc_ntag4xx"),
            ("applications/main/nfc/application.fam", "nfc_type_4_tag"),
            ("applications/main/subghz/application.fam", "subghz_gps"),
            ("applications/system/js_app/application.fam", "js_storage"),
            ("applications/system/js_app/application.fam", "js_usbdisk"),
            ("applications/external/usb_ethernet/application.fam", "cli_ping"),
        )
        for path, appid in plugins:
            with self.subTest(appid=appid):
                self.assert_manifest_app(path, appid, "PLUGIN")

    def test_infrared_fap_consumes_its_embedded_read_only_assets(self) -> None:
        path = "applications/main/infrared/application.fam"
        manifest = self.read(path)
        self.assertIn('fap_file_assets="resources/infrared"', manifest)
        self.assertTrue((ROOT / path).parent.joinpath("resources/infrared").is_dir())
        infrared_scenes = ROOT / "applications/main/infrared/scenes"
        referenced_assets = set()
        for scene in infrared_scenes.glob("infrared_scene_universal_*.c"):
            source = scene.read_text(encoding="utf-8")
            self.assertNotIn('EXT_PATH("infrared/assets/', source, scene.name)
            for asset in source.split('APP_ASSETS_PATH("')[1:]:
                relative = asset.split('"', 1)[0]
                referenced_assets.add(relative)
                self.assertTrue(
                    (ROOT / "applications/main/infrared/resources/infrared" / relative).is_file(),
                    f"{scene.name} references missing embedded asset {relative}",
                )
        self.assertEqual(
            referenced_assets,
            {
                "assets/ac.ir",
                "assets/audio.ir",
                "assets/bluray_dvd.ir",
                "assets/digital_sign.ir",
                "assets/fans.ir",
                "assets/leds.ir",
                "assets/monitor.ir",
                "assets/projectors.ir",
                "assets/tv.ir",
            },
        )

    def test_documented_host_automation_exists(self) -> None:
        paths = (
            "scripts/flipper_warp_cli.py",
            "scripts/warp_app_manager.py",
            "scripts/install-flipper-auto-ethernet.sh",
            ".ai/esp_mcp_orchestrator",
            ".ai/scripts/orchestrator.py",
            ".ai/scripts/sync_submodules.py",
            ".ai/scripts/task_router.py",
            ".ai/scripts/notify.py",
            ".ai/strawberry",
            ".ai/mcp/servers/esp_mcp",
            "tools/fz",
        )
        for relative in paths:
            with self.subTest(path=relative):
                self.assertTrue((ROOT / relative).exists(), relative)

    def test_cli_free_fal_imports_are_exported(self) -> None:
        symbols = self.read("targets/f7/api_symbols.csv")
        self.assertIn("Function,+,memmgr_pool_get_free,size_t,", symbols)
        self.assertIn("Function,+,memmgr_pool_get_max_block,size_t,", symbols)


if __name__ == "__main__":
    unittest.main()
