#!/usr/bin/env python3

import logging
import os
import pathlib
import time

from flipper.app import App
from flipper.storage import FlipperStorage, FlipperStorageOperations
from flipper.utils.cdc import resolve_port


class Main(App):
    APP_POST_CLOSE_DELAY_SEC = 0.2

    def init(self):
        self.parser.add_argument("-p", "--port", help="CDC Port", default="auto")

        self.parser.add_argument("manifest_path", help="Manifest path")
        self.parser.add_argument(
            "--pkg_dir_name", help="Update dir name", default=None, required=False
        )
        self.parser.set_defaults(func=self.install)

        # logging
        self.logger = logging.getLogger()

    def install(self):
        if not (port := resolve_port(self.logger, self.args.port)):
            return 1

        if not os.path.isfile(self.args.manifest_path):
            self.logger.error("Error: manifest not found")
            return 2

        manifest_path = pathlib.Path(os.path.abspath(self.args.manifest_path))
        manifest_name, pkg_name = manifest_path.parts[-1], manifest_path.parts[-2]

        pkg_dir_name = self.args.pkg_dir_name or pkg_name
        update_root = "/ext/update"
        flipper_update_path = f"{update_root}/{pkg_dir_name}"

        self.logger.info(f'Installing "{pkg_name}" from {flipper_update_path}')

        try:
            with FlipperStorage(port) as storage:
                storage_ops = FlipperStorageOperations(storage)
                
                # Killer logic: initial breakout
                self.logger.info("Aggressive breakout: Clearing state and rebooting...")
                try:
                    # Flush and Break
                    storage.port.reset_input_buffer()
                    storage.read.buffer.clear()
                    for _ in range(5):
                        storage.send("\x03")
                        time.sleep(0.05)
                    storage.send("\r\n")
                    time.sleep(0.1)
                    
                    # Try to close any app and then reboot
                    storage.send("loader close\r\n")
                    time.sleep(0.1)
                    storage.send("power reboot\r\n")
                    time.sleep(1)
                except:
                    pass
                
                # Wait for device to reboot and port to reappear
                self.logger.info("Waiting for reboot (15s)...")
                storage.stop()
                time.sleep(15)
                
                self.logger.info("Attempting to reconnect...")
                # Re-init storage on the same port
                storage.start()
                self.logger.info("Reconnected. Proceeding with update.")

                self.logger.info("Verifying update path...")
                storage_ops.mkpath(update_root)
                storage_ops.mkpath(flipper_update_path)
                storage_ops.recursive_send(
                    flipper_update_path, manifest_path.parents[0]
                )

                self.logger.info("Executing update install...")
                storage.send(f"update install {flipper_update_path}/{manifest_name}\r")
                
                # Wait for verification message
                result = storage.read.until(storage.CLI_EOL)
                if b"update install" in result: # Consume echo
                    result = storage.read.until(storage.CLI_EOL)
                
                if b"Verifying" not in result:
                    self.logger.error(f"Unexpected response: {result.decode('ascii')}")
                    return 4
                
                self.logger.info("Update started successfully")
                return 0
        except Exception as e:
            self.logger.error(e)
            return 5


if __name__ == "__main__":
    Main()()
