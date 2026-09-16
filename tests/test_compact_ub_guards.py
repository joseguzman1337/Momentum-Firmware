import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]


class CompactUbGuardsTest(unittest.TestCase):
    def test_usb_irq_shared_pointer_values_are_volatile(self):
        source = (ROOT / "targets/f7/furi_hal/furi_hal_usb_cdc.c").read_text()
        self.assertIn("FuriHalUsbInterface* volatile cdc_if_cur", source)
        self.assertIn("CdcCallbacks* volatile callbacks[IF_NUM_MAX]", source)
        self.assertIn("void* volatile cb_ctx[IF_NUM_MAX]", source)
        self.assertNotIn("volatile CdcCallbacks* callbacks[IF_NUM_MAX]", source)


if __name__ == "__main__":
    unittest.main()
