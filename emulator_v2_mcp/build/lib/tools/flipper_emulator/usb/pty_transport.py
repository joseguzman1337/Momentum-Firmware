"""
Virtual Serial Port / PTY Transport for Flipper Zero USB CDC-ACM emulation.
"""

import os
import threading
from typing import Optional, Callable

class VirtualPTYTransport:
    def __init__(self, on_receive_callback: Optional[Callable[[bytes], None]] = None):
        self.master_fd: Optional[int] = None
        self.slave_fd: Optional[int] = None
        self.slave_name: str = ""
        self.symlink_path = "/tmp/flipper_serial"
        self.on_receive = on_receive_callback
        self.running = False
        self.reader_thread: Optional[threading.Thread] = None

    def start(self) -> str:
        try:
            import pty
            self.master_fd, self.slave_fd = pty.openpty()
            self.slave_name = os.ttyname(self.slave_fd)
            try:
                if os.path.islink(self.symlink_path) or os.path.exists(self.symlink_path):
                    os.remove(self.symlink_path)
                os.symlink(self.slave_name, self.symlink_path)
            except Exception:
                pass
            self.running = True
            self.reader_thread = threading.Thread(target=self._read_loop, daemon=True)
            self.reader_thread.start()
            return self.slave_name
        except Exception as e:
            self.slave_name = f"simulated_pipe_pty ({e})"
            return self.slave_name

    def write(self, data: bytes):
        if self.master_fd is not None:
            try:
                os.write(self.master_fd, data)
            except Exception:
                pass

    def _read_loop(self):
        while self.running and self.master_fd is not None:
            try:
                data = os.read(self.master_fd, 1024)
                if data and self.on_receive:
                    self.on_receive(data)
            except Exception:
                break

    def stop(self):
        self.running = False
        if self.master_fd is not None:
            try: os.close(self.master_fd)
            except Exception: pass
            self.master_fd = None
        if self.slave_fd is not None:
            try: os.close(self.slave_fd)
            except Exception: pass
            self.slave_fd = None
        try:
            if os.path.islink(self.symlink_path):
                os.remove(self.symlink_path)
        except Exception:
            pass
