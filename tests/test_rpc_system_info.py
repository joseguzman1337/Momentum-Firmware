from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "applications/services/rpc/rpc_system.c"
PROPERTY_SOURCE = ROOT / "applications/services/rpc/rpc_property.c"


def _function(source: str, name: str, next_name: str) -> str:
    start_match = re.search(rf"static void\s+{re.escape(name)}", source)
    assert start_match
    end_match = re.search(rf"static void\s+{re.escape(next_name)}", source[start_match.end() :])
    assert end_match
    start = start_match.start()
    end = start_match.end() + end_match.start()
    return source[start:end]


def test_device_info_reinitializes_every_streamed_response():
    source = SOURCE.read_text(encoding="utf-8")
    callback = _function(
        source,
        "rpc_system_system_device_info_callback",
        "rpc_system_system_device_info_process",
    )
    reset = callback.index("*ctx->response = (PB_Main)PB_Main_init_zero;")
    command_id = callback.index("ctx->response->command_id = ctx->command_id;")
    tag = callback.index("PB_Main_system_device_info_response_tag")
    payload = callback.index("content.system_device_info_response.key")
    send = callback.index("rpc_send_and_release")
    assert reset < command_id < tag < payload < send


def test_power_info_reinitializes_every_streamed_response_and_uses_power_union():
    source = SOURCE.read_text(encoding="utf-8")
    callback = _function(
        source,
        "rpc_system_system_power_info_callback",
        "rpc_system_system_get_power_info_process",
    )
    reset = callback.index("*ctx->response = (PB_Main)PB_Main_init_zero;")
    command_id = callback.index("ctx->response->command_id = ctx->command_id;")
    tag = callback.index("PB_Main_system_power_info_response_tag")
    payload = callback.index("content.system_power_info_response.key")
    send = callback.index("rpc_send_and_release")
    assert reset < command_id < tag < payload < send
    assert "content.system_device_info_response" not in callback


def test_info_context_preserves_command_id_across_callback_resets():
    source = SOURCE.read_text(encoding="utf-8")
    assert "uint32_t command_id;" in source
    assert source.count(".command_id = request->command_id,") == 2


def test_property_get_reinitializes_each_response_and_uses_property_union():
    source = PROPERTY_SOURCE.read_text(encoding="utf-8")
    callback = _function(
        source,
        "rpc_system_property_get_callback",
        "rpc_system_property_get_process",
    )
    reset = callback.index("*response = (PB_Main)PB_Main_init_zero;")
    command_id = callback.index("response->command_id = ctx->command_id;")
    tag = callback.index("PB_Main_property_get_response_tag")
    payload = callback.index("content.property_get_response.key")
    send = callback.index("rpc_send_and_release(session, response)")
    assert reset < command_id < tag < payload < send
    assert "content.system_device_info_response" not in callback
    assert "rpc_send_and_release_empty(session, ctx->command_id" in callback
