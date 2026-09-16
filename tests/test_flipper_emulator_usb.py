import os
import select
import tempfile
import time
import unittest
from pathlib import Path

from tools.flipper_emulator.internal_flash import InternalFlashStore
from tools.flipper_emulator.usb.device import VirtualFlipperRpc
from tools.flipper_emulator.usb.protocol import DelimitedDecoder, delimited, field_bytes, field_varint, fields
from tools.flipper_emulator.usb.service import VirtualCdcService


class InternalFlashTests(unittest.TestCase):
    def test_persists_sanitized_defaults(self):
        with tempfile.TemporaryDirectory() as directory:
            image = Path(directory) / "internal.json"
            flash = InternalFlashStore(image)
            flash.write("/int/.desktop.settings", b"changed")
            self.assertEqual(InternalFlashStore(image).read("/int/.desktop.settings"), b"changed")
            text = image.read_text()
            self.assertIn('"sanitized": true', text)
            self.assertNotIn("uid", text.lower())

    def test_rejects_identity_and_pairing_paths(self):
        with tempfile.TemporaryDirectory() as directory:
            flash = InternalFlashStore(Path(directory) / "internal.json")
            for path in ("/int/.bt.settings", "/int/pairing.keys", "/ext/file"):
                with self.assertRaises(ValueError):
                    flash.write(path, b"no")


class RpcTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.device = VirtualFlipperRpc(Path(self.temp.name) / "internal.json", b"x" * 1024)

    def tearDown(self):
        self.temp.cleanup()

    def decode_one(self, response):
        decoded = DelimitedDecoder().feed(response)
        self.assertEqual(len(decoded), 1)
        return fields(decoded[0])

    def test_ping_uses_official_pb_main_tags(self):
        request = field_varint(1, 7) + field_bytes(5, field_bytes(1, b"ping"))
        response = self.decode_one(self.device.handle(request)[0])
        self.assertIn((1, 0, 7), response)
        self.assertTrue(any(number == 6 and wire == 2 for number, wire, _ in response))

    def test_screen_stream_returns_exact_frame(self):
        request = field_varint(1, 9) + field_bytes(20, b"")
        responses = self.device.handle(request)
        self.assertEqual(len(responses), 2)
        frame_main = self.decode_one(responses[1])
        frame = next(value for number, wire, value in frame_main if number == 22 and wire == 2)
        self.assertIn((1, 2, b"x" * 1024), fields(frame))

    def test_int_list_has_no_identity_files(self):
        request = field_varint(1, 2) + field_bytes(7, field_bytes(1, b"/int"))
        raw = self.device.handle(request)[0]
        self.assertNotIn(b"bt", raw.lower())
        self.assertNotIn(b"uid", raw.lower())


class CdcServiceTests(unittest.TestCase):
    def test_pty_cli_to_rpc_handshake(self):
        with tempfile.TemporaryDirectory() as directory:
            service = VirtualCdcService(Path(directory) / "internal.json")
            path = service.start()
            descriptor = os.open(path, os.O_RDWR | os.O_NOCTTY | os.O_NONBLOCK)
            try:
                os.write(descriptor, b"\r")
                self.assertEqual(self._read(descriptor), b">: ")
                os.write(descriptor, b"start_rpc_session\r")
                self.assertEqual(self._read(descriptor), b"start_rpc_session\r\n")
                ping = field_varint(1, 3) + field_bytes(5, field_bytes(1, b"ok"))
                os.write(descriptor, delimited(ping))
                response = DelimitedDecoder().feed(self._read(descriptor))
                self.assertEqual(len(response), 1)
                self.assertIn((1, 0, 3), fields(response[0]))
            finally:
                os.close(descriptor)
                service.close()

    @staticmethod
    def _read(descriptor):
        deadline = time.monotonic() + 2
        data = bytearray()
        while time.monotonic() < deadline:
            ready, _, _ = select.select([descriptor], [], [], 0.05)
            if ready:
                data.extend(os.read(descriptor, 65536))
                if data:
                    return bytes(data)
        raise TimeoutError


if __name__ == "__main__":
    unittest.main()
