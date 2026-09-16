from __future__ import annotations

import os
import pty
import select
import threading
import tty
from pathlib import Path

from .device import VirtualFlipperRpc
from .protocol import DelimitedDecoder


class VirtualCdcService:
    """PTY-backed CDC endpoint: CLI handshake, then binary delimited RPC."""

    def __init__(self, flash_image: Path, framebuffer: bytes | None = None):
        self.device = VirtualFlipperRpc(flash_image, framebuffer)
        self.master, self.slave = pty.openpty()
        tty.setraw(self.slave)
        self.path = os.ttyname(self.slave)
        self._stop = threading.Event()
        self._thread: threading.Thread | None = None

    def start(self) -> str:
        self._thread = threading.Thread(target=self._serve, name="virtual-flipper-cdc", daemon=True)
        self._thread.start()
        return self.path

    def _serve(self) -> None:
        decoder = DelimitedDecoder()
        rpc = False
        line = bytearray()
        while not self._stop.is_set():
            ready, _, _ = select.select([self.master], [], [], 0.1)
            if not ready:
                continue
            data = os.read(self.master, 65536)
            if not data:
                break
            if not rpc:
                line.extend(data)
                if b"start_rpc_session\r" in line or b"start_rpc_session\n" in line:
                    os.write(self.master, b"start_rpc_session\r\n")
                    rpc = True
                elif b"\r" in line or b"\n" in line:
                    os.write(self.master, b">: ")
                    line.clear()
            else:
                for message in decoder.feed(data):
                    for response in self.device.handle(message):
                        os.write(self.master, response)

    def close(self) -> None:
        self._stop.set()
        if self._thread:
            self._thread.join(timeout=1)
        os.close(self.master)
        os.close(self.slave)

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, *_args):
        self.close()
