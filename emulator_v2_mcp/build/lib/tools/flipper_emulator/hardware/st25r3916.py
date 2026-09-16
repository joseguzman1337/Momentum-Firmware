"""
ST25R3916 13.56 MHz NFC and 125 kHz LF-RFID Frontend Emulation.
"""

from typing import Dict, List, Optional, Any

class NFCRFIDController:
    def __init__(self):
        self.nfc_active = False
        self.rfid_active = False
        self.active_nfc_card: Optional[Dict[str, Any]] = None
        self.active_rfid_tag: Optional[Dict[str, Any]] = None

    def read_nfc(self, card_type: str = "Mifare Classic", uid: str = "04 A1 B2 C3 D4 E5 F6", atqa: str = "00 04", sak: str = "08") -> Dict[str, Any]:
        return {
            "type": card_type, "uid": uid, "atqa": atqa, "sak": sak,
            "data_blocks": 64 if "Classic" in card_type else 135
        }

    def emulate_nfc(self, uid: str, card_type: str = "Mifare Classic", sak: str = "08", atqa: str = "00 04"):
        self.nfc_active = True
        self.active_nfc_card = {"uid": uid, "type": card_type, "sak": sak, "atqa": atqa, "emulating": True}

    def stop_nfc_emulation(self):
        self.nfc_active = False
        self.active_nfc_card = None

    def read_rfid(self, protocol: str = "EM4100", data_hex: str = "01 02 03 04 05") -> Dict[str, Any]:
        return {"protocol": protocol, "data": data_hex, "frequency_khz": 125}

    def emulate_rfid(self, protocol: str, data_hex: str):
        self.rfid_active = True
        self.active_rfid_tag = {"protocol": protocol, "data": data_hex, "emulating": True}

    def stop_rfid_emulation(self):
        self.rfid_active = False
        self.active_rfid_tag = None

    def get_status(self) -> Dict[str, Any]:
        return {
            "nfc": {"active": self.nfc_active, "emulating_card": self.active_nfc_card},
            "rfid": {"active": self.rfid_active, "emulating_tag": self.active_rfid_tag}
        }
