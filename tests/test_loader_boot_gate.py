import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
LOADER = ROOT / "applications/services/loader/loader.c"
FIRMWARE_OPTS = ROOT / "site_scons/firmwareopts.scons"


class LoaderBootGateTest(unittest.TestCase):
    def test_automatic_overlay_is_enabled_and_state_is_initialized(self):
        source = LOADER.read_text()
        self.assertIn("#define LOADER_AUTO_LOADING_ENABLED 1", source)
        for initialization in (
            "loader->loading_timer = NULL;",
            "loader->loading_hold_start = 0;",
            "loader->loading_view_ports_baseline = 0;",
            "loader->loading_depth = 0;",
            "loader->loading_held = false;",
        ):
            self.assertIn(initialization, source)

        dispatcher = (ROOT / "applications/services/gui/view_dispatcher.c").read_text()
        self.assertIn("view_dispatcher->loading = NULL;", dispatcher)

    def test_loading_failures_are_nonfatal(self):
        source = LOADER.read_text()
        self.assertIn("Load depth overflow", source)
        self.assertIn("Load hide unbalanced", source)
        self.assertNotIn("furi_check(loader->loading_depth", source)

    def test_loading_api_is_preserved(self):
        header = (ROOT / "applications/services/gui/modules/loading.h").read_text()
        for symbol in (
            "loading_set_progress(",
            "loading_set_progress_ratio(",
            "loading_reset_progress(",
        ):
            self.assertIn(symbol, header)

    def test_alignment_sort_preserves_c2_headroom(self):
        self.assertIn("--sort-section=alignment", FIRMWARE_OPTS.read_text())


if __name__ == "__main__":
    unittest.main()
