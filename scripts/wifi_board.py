#!/usr/bin/env python3

import json
import logging
import os
import subprocess
import tarfile
import tempfile
from typing import Any, Dict, List, Optional

import requests
import serial.tools.list_ports as list_ports
from flipper.app import App
from serial.tools.list_ports_common import ListPortInfo


class UpdateDownloader:
    """Download and unpack WiFi board firmware archives from the update server."""

    UPDATE_SERVER = "https://update.flipperzero.one"
    UPDATE_PROJECT = "/blackmagic-firmware"
    UPDATE_INDEX = UPDATE_SERVER + UPDATE_PROJECT + "/directory.json"
    UPDATE_TYPE = "full_tgz"

    CHANNEL_ID_ALIAS: Dict[str, str] = {
        "dev": "development",
        "rc": "release-candidate",
        "r": "release",
        "rel": "release",
    }

    def __init__(self) -> None:
        self.logger = logging.getLogger(__name__)

    def download(self, channel_id: str, target_dir: str) -> bool:
        """Download and unpack update for the given channel into target_dir.

        Returns True on success and False on any error. All user-visible errors are
        logged via the instance logger.
        """
        # Aliases
        if channel_id in self.CHANNEL_ID_ALIAS:
            channel_id = self.CHANNEL_ID_ALIAS[channel_id]

        # Make directory
        if not os.path.exists(target_dir):
            self.logger.info(f"Creating directory %s", target_dir)
            os.makedirs(target_dir, exist_ok=True)

        # Download json index
        self.logger.info("Downloading %s", self.UPDATE_INDEX)
        try:
            response = requests.get(self.UPDATE_INDEX, timeout=15)
            response.raise_for_status()
        except requests.RequestException as e:
            self.logger.error("Failed to download %s: %s", self.UPDATE_INDEX, e)
            return False

        # Parse json index
        try:
            index: Dict[str, Any] = json.loads(response.content)
        except Exception as e:  # pragma: no cover - defensive logging
            self.logger.error("Failed to parse json index: %s", e)
            return False

        channels = index.get("channels")
        if not isinstance(channels, list):
            self.logger.error("Invalid update index: 'channels' key is missing or malformed")
            return False

        # Find channel
        channel: Optional[Dict[str, Any]] = None
        for channel_candidate in channels:
            if not isinstance(channel_candidate, dict):
                continue
            if channel_candidate.get("id") == channel_id:
                channel = channel_candidate
                break

        # Check if channel found
        if channel is None:
            valid_ids = [str(c.get("id")) for c in channels if isinstance(c, dict)]
            self.logger.error(
                "Channel '%s' not found. Valid channels: %s", channel_id, ", ".join(valid_ids)
            )
            return False

        self.logger.info("Using channel '%s'", channel_id)

        # Get latest version
        try:
            versions = channel["versions"]
            if not isinstance(versions, list) or not versions:
                raise ValueError("'versions' is empty or not a list")
            version: Dict[str, Any] = versions[0]
        except Exception as e:  # pragma: no cover - defensive logging
            self.logger.error("Failed to get version: %s", e)
            return False

        self.logger.info("Using version '%s'", version.get("version", "unknown"))

        # Get changelog
        changelog = version.get("changelog")
        if isinstance(changelog, str) and changelog.strip():
            self.logger.info("Changelog:")
            for line in changelog.split("\n"):
                if line.strip() == "":
                    continue
                self.logger.info("  %s", line)
        else:
            self.logger.warning("Changelog not found")

        # Find file
        file_url: Optional[str] = None
        files = version.get("files")
        if isinstance(files, list):
            for file_candidate in files:
                if not isinstance(file_candidate, dict):
                    continue
                if file_candidate.get("type") == self.UPDATE_TYPE:
                    file_url = file_candidate.get("url")
                    break

        if not file_url:
            self.logger.error("File of type '%s' not found in version metadata", self.UPDATE_TYPE)
            return False

        # Make file path
        file_name = file_url.split("/")[-1]
        file_path = os.path.join(target_dir, file_name)

        # Download file
        self.logger.info("Downloading %s to %s", file_url, file_path)
        try:
            response = requests.get(file_url, timeout=60)
            response.raise_for_status()
        except requests.RequestException as e:
            self.logger.error("Failed to download %s: %s", file_url, e)
            return False

        with open(file_path, "wb") as f:
            f.write(response.content)

        # Unzip tgz
        self.logger.info("Unzipping %s", file_path)
        try:
            with tarfile.open(file_path, "r") as tar:
                # Secure extraction: validate all members before extracting
                def is_within_directory(directory: str, target: str) -> bool:
                    abs_directory = os.path.abspath(directory)
                    abs_target = os.path.abspath(target)
                    return os.path.commonprefix([abs_directory, abs_target]) == abs_directory

                def safe_extract(archive: tarfile.TarFile, path: str) -> None:
                    for member in archive.getmembers():
                        member_path = os.path.join(path, member.name)
                        if not is_within_directory(path, member_path):
                            raise RuntimeError(
                                f"Attempted path traversal in tar file: {member.name}"
                            )
                    archive.extractall(path)

                safe_extract(tar, target_dir)
        except (tarfile.TarError, OSError, RuntimeError) as e:
            self.logger.error("Failed to unpack archive %s: %s", file_path, e)
            return False

        return True


class Main(App):
    """CLI helper used to flash the WiFi board firmware over serial."""

    def init(self) -> None:
        self.parser.add_argument("-p", "--port", help="CDC Port", default="auto")
        self.parser.add_argument(
            "-c", "--channel", help="Channel name", default="release"
        )
        self.parser.set_defaults(func=self.update)

        # logging
        self.logger = logging.getLogger(__name__)

    @staticmethod
    def _grep_ports(regexp: str) -> List[ListPortInfo]:
        """Return a list of serial ports matching the given regular expression."""
        # idk why, but python thinks that list_ports.grep returns tuple[str, str, str]
        return list(list_ports.grep(regexp))  # type: ignore[arg-type]

    def is_wifi_board_connected(self) -> bool:
        return (
            len(self._grep_ports("ESP32-S2")) > 0
            or len(self._grep_ports("CMSIS-DAP")) > 0
        )

    @staticmethod
    def is_windows() -> bool:
        return os.name == "nt"

    @classmethod
    def find_port(cls, regexp: str) -> Optional[str]:
        ports: List[ListPortInfo] = cls._grep_ports(regexp)

        if len(ports) == 0:
            # Blackmagic probe serial port not found, will be handled later
            return None
        if len(ports) > 1:
            raise RuntimeError("More than one WiFi board found")

        port = ports[0]
        return f"\\\\.\\{port.device}" if cls.is_windows() else port.device

    def find_wifi_board_bootloader_port(self) -> Optional[str]:
        return self.find_port("ESP32-S2")

    def find_wifi_board_bootloader_port_damn_windows(self) -> Optional[str]:
        self.logger.info("Trying to find WiFi board using VID:PID")
        return self.find_port("VID:PID=303A:0002")

    def update(self) -> int:
        try:
            port = self.find_wifi_board_bootloader_port()

            # Damn windows fix
            if port is None and self.is_windows():
                port = self.find_wifi_board_bootloader_port_damn_windows()
        except Exception as e:  # pragma: no cover - extremely unlikely branch
            self.logger.error("%s", e)
            return 1

        if port is None:
            if self.is_wifi_board_connected():
                self.logger.error("WiFi board found, but not in bootloader mode.")
                self.logger.info("Please hold down BOOT button and press RESET button")
            else:
                self.logger.error("WiFi board not found")
                self.logger.info(
                    "Please connect WiFi board to your computer, hold down BOOT button and press RESET button"
                )
                if not self.is_windows():
                    self.logger.info(
                        "If you are using Linux, you may need to add udev rules to access the device"
                    )
                    self.logger.info(
                        "Check out 41-flipper.rules & README in scripts/debug folder"
                    )
            return 1

        # get temporary dir
        with tempfile.TemporaryDirectory() as temp_dir:
            downloader = UpdateDownloader()

            # download latest channel update
            try:
                if not downloader.download(self.args.channel, temp_dir):
                    self.logger.error("Cannot download update")
                    return 1
            except Exception as e:  # pragma: no cover - defensive logging
                self.logger.error("Cannot download update: %s", e)
                return 1

            with open(os.path.join(temp_dir, "flash.command"), "r", encoding="utf-8") as f:
                flash_command = f.read()

            replacements = (
                ("\n", ""),
                ("\r", ""),
                ("(PORT)", port),
                # We can't reset the board after flashing via usb
                ("--after hard_reset", "--after no_reset_stub"),
            )

            # hellish toolchain fix
            if self.is_windows():
                replacements += (("esptool.py", "python -m esptool"),)
            else:
                replacements += (("esptool.py", "python3 -m esptool"),)

            for old, new in replacements:
                flash_command = flash_command.replace(old, new)

            args = list(filter(None, flash_command.split()))

            self.logger.info('Running command: "%s" in "%s"', " ".join(args), temp_dir)

            process = subprocess.Popen(
                args,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                cwd=temp_dir,
                bufsize=1,
                universal_newlines=True,
            )

            assert process.stdout is not None
            for line in process.stdout:
                self.logger.debug(line.strip())

        if process.returncode != 0:
            self.logger.error("Failed to flash WiFi board")
        else:
            self.logger.info("WiFi board flashed successfully")
            self.logger.info("Press RESET button on WiFi board to start it")

        return int(process.returncode)


if __name__ == "__main__":
    Main()()
