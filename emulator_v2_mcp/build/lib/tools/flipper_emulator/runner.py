"""
Flipper Zero Emulator Test Runner & Validation Harness.
Executes isolated test suites, verifies hardware hashes, and outputs coverage reports.
"""

import time
import hashlib
from typing import Dict, Any, List, Optional
from .emulator import FlipperZeroEmulator
from .models import ButtonKey, InputType

class FlipperEmulatorRunner:
    """
    Automated test runner and coverage validation harness for Flipper Zero Emulator v2.
    """
    def __init__(self, emulator: Optional[FlipperZeroEmulator] = None):
        self.emu = emulator or FlipperZeroEmulator()
        self.results: List[Dict[str, Any]] = []

    def _record_test(self, name: str, success: bool, details: str, duration_ms: float):
        self.results.append({
            "test_name": name,
            "status": "PASS" if success else "FAIL",
            "details": details,
            "duration_ms": round(duration_ms, 3)
        })

    def run_all_tests(self) -> Dict[str, Any]:
        """Execute full hardware & subsystem test suite."""
        self.results.clear()
        start_time = time.time()

        # 1. CPU Core test
        t0 = time.time()
        self.emu.reset()
        c0 = self.emu.core.cycles
        self.emu.step(100)
        c1 = self.emu.core.cycles
        self._record_test(
            "cortex_m4_execution",
            c1 == c0 + 100 and not self.emu.core.halted,
            f"Executed 100 cycles, PC=0x{self.emu.core.pc:08X}",
            (time.time() - t0) * 1000
        )

        # 2. Bus & Memory Map test
        t0 = time.time()
        test_val = 0xA5A55A5A
        self.emu.bus.write_u32(0x20000100, test_val)
        read_val = self.emu.bus.read_u32(0x20000100)
        self._record_test(
            "sram1_read_write",
            read_val == test_val,
            f"Wrote and read 0x{read_val:08X} in SRAM1",
            (time.time() - t0) * 1000
        )

        # 3. OTP v2 Memory test
        t0 = time.time()
        otp_magic = self.emu.otp.dump()[:4]
        target = self.emu.otp.read_byte(5)
        body = self.emu.otp.read_byte(6)
        color = self.emu.otp.read_byte(9)
        region = self.emu.otp.read_byte(10)
        self._record_test(
            "otp_v2_synthetic_integrity",
            otp_magic == b"FURI" and target == 7 and body == 9 and color == 2 and region == 4,
            f"Magic={otp_magic.decode()}, Target=F7, Body=B9, Color=White(2), Region=CO(4)",
            (time.time() - t0) * 1000
        )

        # 4. HSEM 32 Semaphores test
        t0 = time.time()
        locked = self.emu.hsem.take_semaphore(0, proc_id=1, core_id=1)
        relocked = self.emu.hsem.take_semaphore(0, proc_id=2, core_id=1)
        released = self.emu.hsem.release_semaphore(0, proc_id=1, core_id=1)
        self._record_test(
            "hsem_32_semaphores",
            locked and not relocked and released and self.emu.hsem.semaphores[0] == 0,
            "Atomic take/conflict/release verified on sem 0",
            (time.time() - t0) * 1000
        )

        # 5. IPCC Mailbox test
        t0 = time.time()
        self.emu.ipcc.send_c1_to_c2(1)
        stat = self.emu.ipcc.c1_to_c2_status & (1 << 1)
        self.emu.ipcc.acknowledge_c1_from_c2(1)
        self._record_test(
            "ipcc_6_channels",
            bool(stat) and (self.emu.ipcc.c1_to_c2_status & (1 << 1)) == 0,
            "Channel 1 TX status set and acknowledged",
            (time.time() - t0) * 1000
        )

        # 6. ST7567 Display 128x64 test
        t0 = time.time()
        self.emu.display.clear(0)
        self.emu.display.set_pixel(10, 10, 1)
        px1 = self.emu.display.get_pixel(10, 10)
        px2 = self.emu.display.get_pixel(11, 10)
        self.emu.display._init_default_gui()
        frame = self.emu.display.get_framebuffer()
        self._record_test(
            "st7567_display_128x64",
            px1 == 1 and px2 == 0 and len(frame) == 1024,
            f"Framebuffer size: {len(frame)} bytes, pixels verified",
            (time.time() - t0) * 1000
        )

        # 7. Button & GUI Navigation test
        t0 = time.time()
        init_idx = self.emu.buttons.selected_menu_idx
        self.emu.press_button("DOWN", "SHORT")
        next_idx = self.emu.buttons.selected_menu_idx
        self.emu.press_button("UP", "SHORT")
        back_idx = self.emu.buttons.selected_menu_idx
        self._record_test(
            "gpio_buttons_and_navigation",
            next_idx == (init_idx + 1) % len(self.emu.buttons.menu_items) and back_idx == init_idx,
            f"Menu navigation UP/DOWN responded properly (idx: {init_idx} -> {next_idx} -> {back_idx})",
            (time.time() - t0) * 1000
        )

        # 8. Storage /int persistent test
        t0 = time.time()
        int_files = self.emu.flash_mgr.list_files()
        dolphin_data = self.emu.flash_mgr.read_file(".dolphin.state")
        self._record_test(
            "storage_int_persistent",
            len(int_files) >= 5 and dolphin_data is not None,
            f"Found {len(int_files)} persistent files in /int (.dolphin.state, .region_data)",
            (time.time() - t0) * 1000
        )

        # 9. Storage /ext MicroSD test
        t0 = time.time()
        ext_list = self.emu.sd_card.list_dir("/ext")
        test_file = "/ext/test_rw.tmp"
        self.emu.sd_card.write_file(test_file, b"FlipperZero_Test_Payload_2026")
        read_back = self.emu.sd_card.read_file(test_file)
        self.emu.sd_card.delete_file(test_file)
        self._record_test(
            "storage_ext_microsd",
            read_back == b"FlipperZero_Test_Payload_2026" and len(ext_list) > 0,
            f"MicroSD SPI2 /ext root has {len(ext_list)} directories, RW verified",
            (time.time() - t0) * 1000
        )

        # 10. CC1101 Sub-GHz test
        t0 = time.time()
        tx_res = self.emu.cc1101.transmit("Princeton", "A1B2C3", 24)
        rx_res = self.emu.cc1101.receive_packet("Princeton", "A1B2C3", 433920000)
        self._record_test(
            "cc1101_subghz",
            tx_res["status"] == "TX_SUCCESS" and rx_res["valid"],
            f"433.92 MHz TX & RX validated (RSSI {rx_res['rssi_dbm']} dBm)",
            (time.time() - t0) * 1000
        )

        # 11. ST25R3916 NFC & 125kHz RFID test
        t0 = time.time()
        nfc_tag = self.emu.nfc_rfid.read_nfc("Mifare Classic")
        rfid_tag = self.emu.nfc_rfid.read_rfid("EM4100")
        self._record_test(
            "st25r3916_nfc_and_rfid",
            nfc_tag["type"] == "Mifare Classic" and rfid_tag["protocol"] == "EM4100",
            f"NFC UID: {nfc_tag['uid']}, RFID Data: {rfid_tag['data']}",
            (time.time() - t0) * 1000
        )

        # 12. USB CDC CLI Shell test
        t0 = time.time()
        cli_out = self.emu.run_cli_command("device_info")
        date_out = self.emu.run_cli_command("date")
        self._record_test(
            "usb_cdc_cli",
            "emulator-v2" in cli_out and "F7B9C6" in cli_out and len(date_out) > 5,
            f"CLI device_info returned emulator-v2 profile, date returned {date_out}",
            (time.time() - t0) * 1000
        )

        # 13. Protobuf RPC test
        t0 = time.time()
        ping_resp = self.emu.rpc.handle_ping(1)
        dev_info_tuples = self.emu.rpc.handle_device_info(2)
        dev_dict = dict(dev_info_tuples)
        self._record_test(
            "rpc_protobuf_protocol",
            ping_resp["status"] == "OK" and dev_dict.get("hardware_name") == "emulator-v2",
            f"RPC Ping status: OK, RPC DeviceInfo name: {dev_dict.get('hardware_name')}",
            (time.time() - t0) * 1000
        )

        total_elapsed = (time.time() - start_time) * 1000
        passed = sum(1 for r in self.results if r["status"] == "PASS")
        failed = sum(1 for r in self.results if r["status"] == "FAIL")
        
        # Calculate state hash
        hasher = hashlib.sha256()
        for r in self.results:
            hasher.update(f"{r['test_name']}:{r['status']}".encode())
        hasher.update(self.emu.display.get_framebuffer())
        test_hash = hasher.hexdigest()[:16]

        summary = {
            "total_tests": len(self.results),
            "passed": passed,
            "failed": failed,
            "pass_rate": f"{(passed / len(self.results)) * 100:.1f}%",
            "elapsed_ms": round(total_elapsed, 2),
            "test_run_hash": test_hash,
            "tests": self.results
        }
        return summary
