#!/usr/bin/env python3

import logging
import os
import pathlib
import sys
import time

from flipper.app import App
from flipper.storage import FlipperStorage, FlipperStorageOperations
from flipper.utils.cdc import resolve_port


class Main(App):
    APP_POST_CLOSE_DELAY_SEC = 0.2
    CONNECT_RETRY_DELAY_SEC = 1.0
    CONNECT_RETRIES = 15

    def init(self):
        self.parser.add_argument("-p", "--port", help="CDC Port", default="auto")
        self.parser.add_argument(
            "--plain",
            action="store_true",
            help="Disable ANSI colors / pretty output",
            default=False,
        )

        self.parser.add_argument("manifest_path", help="Manifest path")
        self.parser.add_argument(
            "--pkg_dir_name", help="Update dir name", default=None, required=False
        )
        self.parser.set_defaults(func=self.install)

        # logging
        self.logger = logging.getLogger()

        # output mode flag; finalized in install() after args are parsed
        self.pretty = False
        self.debug_io = True

    def _log_step(self, label: str, detail: str = ""):
        if self.pretty:
            prefix = "\033[36m\033[1m::\033[0m\033[1m"
            msg = f"{prefix} {label}\033[0m"
            if detail:
                msg += f" {detail}"
            print(msg)
        else:
            print(f":: {label} {detail}")

    def _log_ok(self, msg: str):
        if self.pretty:
            print("\033[32m\033[1m  \xE2\x9C\x93 \033[0m" + msg)
        else:
            print(f"[OK] {msg}")

    def _log_err(self, msg: str):
        if self.pretty:
            print("\033[31m\033[1m  \xE2\x9C\x97 \033[0m" + msg)
        else:
            print(f"[ERR] {msg}")

    def _log_debug(self, msg: str):
        if not self.debug_io:
            return
        if self.pretty:
            print(f"\033[90m{msg}\033[0m")
        else:
            print(msg)

    def _read_line(self, storage, label: str):
        result = storage.read.until(storage.CLI_EOL)
        result_str = result.decode("ascii", errors="ignore").strip()
        self._log_debug(f"[serial] {label}: {result_str}")
        return result, result_str

    def _port_transport(self, port: str) -> str:
        port_lower = port.lower()
        if "usbmodem" in port_lower or "ttyacm" in port_lower:
            return "usb-c cdc"
        if "ttyusb" in port_lower or "usbserial" in port_lower or "com" in port_lower:
            return "serial"
        return "unknown"

    def install(self):
        # Determine pretty mode now that arguments are parsed
        self.pretty = sys.stdout.isatty() and not self.args.plain

        retries = int(os.environ.get("FBT_SELFUPDATE_RETRIES", self.CONNECT_RETRIES))
        delay = float(os.environ.get("FBT_SELFUPDATE_RETRY_DELAY", self.CONNECT_RETRY_DELAY_SEC))

        port = None
        for attempt in range(1, retries + 1):
            port = resolve_port(self.logger, self.args.port)
            if port:
                break
            self._log_step("Waiting", f"for Flipper USB-C ({attempt}/{retries})")
            self._log_debug("[serial] resolve_port returned no device")
            time.sleep(delay)
        if not port:
            self._log_err("Failed to find connected Flipper")
            self.logger.error("Failed to find connected Flipper")
            return 1
        self._log_debug(f"[serial] selected port: {port} ({self._port_transport(port)})")

        if not os.path.isfile(self.args.manifest_path):
            self._log_err("Manifest not found")
            self.logger.error("Error: manifest not found")
            return 2

        manifest_path = pathlib.Path(os.path.abspath(self.args.manifest_path))
        manifest_name, pkg_name = manifest_path.parts[-1], manifest_path.parts[-2]

        pkg_dir_name = self.args.pkg_dir_name or pkg_name
        update_root = "/ext/update"
        flipper_update_path = f"{update_root}/{pkg_dir_name}"

        if self.pretty:
            print("\n\033[1m⚡ FLIPPER USB UPDATE\033[0m")
        self._log_step("SelfUpdate", f'Installing "{pkg_name}"')
        if self.pretty:
            print(f"  \033[90mLocal manifest:\033[0m {manifest_path}")
            print(f"  \033[90mRemote path :\033[0m {flipper_update_path}")
        else:
            print(f"  Local manifest: {manifest_path}")
            print(f"  Remote path : {flipper_update_path}")

        self.logger.info(f'Installing "{pkg_name}" from {flipper_update_path}')

        try:
            self._log_debug(f"[serial] opening FlipperStorage on {port} ({self._port_transport(port)})")
            with FlipperStorage(port) as storage:
                self._log_debug("[serial] FlipperStorage opened")
                storage_ops = FlipperStorageOperations(storage)

                # Pre-requisite: ensure no app is running before we bother sending update data.
                if self.pretty:
                    self._log_step("Loader", "Closing current app, if any")
                self.logger.info("Closing current app, if any")
                for _ in range(10):
                    storage.send_and_wait_eol("loader close\r")
                    _, result_str = self._read_line(storage, "loader close")
                    if "was closed" in result_str:
                        self.logger.info("App closed")
                        self._read_line(storage, "loader close follow-up")
                        time.sleep(self.APP_POST_CLOSE_DELAY_SEC)
                    elif result_str.startswith("No application"):
                        self._read_line(storage, "loader close follow-up")
                        break
                    elif "has to be closed manually" in result_str:
                        # Some apps (like Passport) ignore the exit signal.
                        # Abort early so we don't waste time pushing an update
                        # we already know will fail on the device side.
                        msg = f"App requires manual close ({result_str}); aborting update"
                        self._log_err(msg)
                        self.logger.error(msg)
                        self._read_line(storage, "loader close follow-up")
                        return 4
                    else:
                        self.logger.error(f"Unexpected response from loader close: {result_str}")
                        return 4

                # With no app running, proceed to send update data.
                storage_ops.mkpath(update_root)
                storage_ops.mkpath(flipper_update_path)
                storage_ops.recursive_send(
                    flipper_update_path, manifest_path.parents[0]
                )

                storage.send_and_wait_eol(
                    f"update install {flipper_update_path}/{manifest_name}\r"
                )
                result, result_str = self._read_line(storage, "update install")
                if b"Verifying" not in result:
                    self._log_err(f"Unexpected response: {result_str}")
                    self.logger.error(f"Unexpected response: {result_str}")
                    return 3
                if self.pretty:
                    self._log_step("Device", "Verifying & applying update...")
                result, result_str = self._read_line(storage, "update result")
                if not result.startswith(b"OK"):
                    self._log_err(result_str)
                    self.logger.error(result_str)
                    return 4
                self._log_ok("Update triggered successfully. Device will reboot.")
                return 0
        except Exception as e:
            self._log_err(str(e))
            self.logger.error(e)
            return 5


if __name__ == "__main__":
    Main()()
