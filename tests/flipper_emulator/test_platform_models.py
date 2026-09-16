import json
from pathlib import Path

import pytest

from tools.flipper_emulator.models import (
    Cpu2Service, HsemModel, IpccModel, ModelError, PublicC2Firmware, SafeDeviceInfo,
)
from tools.flipper_emulator.runner import build_platform_models


def test_hsem_exclusion_and_owner_release():
    hsem = HsemModel()
    assert hsem.take(7, 1)
    assert not hsem.take(7, 2)
    assert not hsem.release(7, 2)
    assert hsem.release(7, 1)
    assert hsem.take(7, 2)


def test_ipcc_is_directional_busy_and_consuming():
    ipcc = IpccModel()
    ipcc.send(1, 3, b"request")
    with pytest.raises(ModelError, match="busy"):
        ipcc.send(1, 3, b"second")
    assert ipcc.receive(1, 3) is None
    assert ipcc.receive(2, 3) == b"request"
    assert ipcc.receive(2, 3) is None


def test_cpu2_fus_radio_state_and_bounded_ble():
    service = Cpu2Service({"radio_alive": "true", "radio_stack_major": "1",
                           "radio_stack_minor": "20", "radio_stack_sub": "0"})
    assert service.command("get_state")["started"] is False
    assert service.command("ble_echo", payload=b"x")["status"] == "unsupported"
    assert service.command("start")["status"] == "ok"
    assert service.command("get_version")["version"] == "1.20.0"
    assert service.command("ble_echo", payload=b"abc")["payload"] == b"abc"
    assert service.command("ble_echo", payload=b"x" * 252)["status"] == "invalid_parameter"


def test_safe_info_rejects_identity_and_option_writes(tmp_path: Path):
    unsafe = tmp_path / "unsafe.json"
    unsafe.write_text(json.dumps({"uid": "not-allowed"}))
    with pytest.raises(ModelError, match="identity-bearing"):
        SafeDeviceInfo.from_json(unsafe)
    with pytest.raises(ModelError, match="read-only"):
        SafeDeviceInfo().write_option_byte("RDP", 0)


def test_public_c2_is_reference_only_and_reported(tmp_path: Path):
    c2 = tmp_path / "public-radio.bin"
    c2.write_bytes(bytes(range(256)) * 8)
    metadata = PublicC2Firmware.inspect(c2)
    assert metadata.bytes == 2048
    assert metadata.executed is False
    result = build_platform_models({"c2_firmware": str(c2)}, None)
    assert result["c2_reference"]["executed"] is False
    assert result["info_table"]["writes_allowed"] is False
