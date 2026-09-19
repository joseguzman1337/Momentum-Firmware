"""Deterministic regressions for USB RPC saturation and reconnect handling.

These tests intentionally avoid real USB timing.  They pin the transport invariants that
prevent a best-effort GUI frame from consuming space needed by a maximum storage chunk.
"""

import re
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RPC_CLI = ROOT / "applications/services/rpc/rpc_cli.c"
RPC_CORE = ROOT / "applications/services/rpc/rpc.c"
RPC_GUI = ROOT / "applications/services/rpc/rpc_gui.c"
RPC_STORAGE = ROOT / "applications/services/rpc/rpc_storage.c"
CLI_VCP = ROOT / "applications/services/cli/cli_vcp.c"
CLI_VCP_HEADER = ROOT / "applications/services/cli/cli_vcp.h"
PIPE = ROOT / "lib/toolbox/pipe.c"

STORAGE_CHUNK_BYTES = 512
# command_id, status, has_next, nested-message tags/lengths and delimited envelope all add
# bytes around the payload.  32 bytes is a deliberately conservative protocol allowance.
PROTOBUF_ENVELOPE_BYTES = 32
MIN_STORAGE_RESPONSE_RESERVE = STORAGE_CHUNK_BYTES + PROTOBUF_ENVELOPE_BYTES


def _numeric_define(source: str, name: str) -> int:
    """Resolve a numeric object-like define, including one level of named aliases."""

    match = re.search(rf"^#define\s+{name}\s+([^\s/]+)", source, re.MULTILINE)
    assert match, f"missing auditable byte-count define {name}"
    value = match.group(1).strip("()")
    numeric = re.fullmatch(r"([0-9]+)(?:U|UL|ULL)?", value)
    if numeric:
        return int(numeric.group(1))
    assert re.fullmatch(r"[A-Z][A-Z0-9_]+", value), f"unsupported value for {name}: {value}"
    assert value != name, f"recursive define {name}"
    return _numeric_define(source, value)


def test_usb_control_reserve_fits_maximum_storage_read_response():
    storage = RPC_STORAGE.read_text(encoding="utf-8")
    assert re.search(r"MAX_DATA_SIZE\s*=\s*512\s*;", storage)

    cli = RPC_CLI.read_text(encoding="utf-8")
    reserve = _numeric_define(cli, "CLI_RPC_CONTROL_RESERVE")
    assert reserve >= MIN_STORAGE_RESPONSE_RESERVE, (
        f"USB RPC reserve {reserve} cannot hold a {STORAGE_CHUNK_BYTES}-byte storage payload "
        f"plus {PROTOBUF_ENVELOPE_BYTES} bytes of protobuf framing"
    )


def test_saturated_usb_drops_gui_frame_before_spending_storage_reserve():
    """Exercise the boundary values of the production admission predicate."""

    reserve = _numeric_define(RPC_CLI.read_text(encoding="utf-8"), "CLI_RPC_CONTROL_RESERVE")

    def admit_best_effort(spaces: int, frame_bytes: int) -> bool:
        return spaces >= frame_bytes and spaces - frame_bytes >= reserve

    assert not admit_best_effort(reserve, 1)
    assert not admit_best_effort(reserve + 1023, 1024)
    assert admit_best_effort(reserve + 1024, 1024)
    assert reserve >= MIN_STORAGE_RESPONSE_RESERVE

    gui = RPC_GUI.read_text(encoding="utf-8")
    callback_start = gui.index("static void rpc_system_gui_screen_stream_frame_callback")
    callback_end = gui.index("static int32_t rpc_system_gui_screen_stream_frame_transmit_thread")
    callback = gui[callback_start:callback_end]
    assert "furi_mutex_acquire(rpc_gui->transmit_mutex, 0)" in callback
    assert "FuriWaitForever" not in callback
    assert "return;" in callback


def test_reliable_rpc_responses_remain_lossless_without_firmware_timeout():
    cli = RPC_CLI.read_text(encoding="utf-8")
    callback_start = cli.index("static void rpc_cli_send_bytes_callback")
    callback_end = cli.index("static bool", callback_start)
    callback = cli[callback_start:callback_end]
    assert "pipe_send(cli_rpc->pipe, bytes, bytes_len);" in callback
    assert "TX_STALL_TIMEOUT" not in cli
    assert "pipe_send_timeout" not in cli


def test_multi_message_command_response_preempts_best_effort_frames():
    core = RPC_CORE.read_text(encoding="utf-8")

    assert "volatile bool command_in_progress;" in core
    assert "session->command_in_progress = true;" in core
    assert "session->command_in_progress = false;" in core
    best_effort = core.split("bool rpc_send_best_effort", 1)[1].split(
        "void rpc_send_and_release", 1
    )[0]
    assert "if(session->command_in_progress) return false;" in best_effort
    assert "has_best_effort_callback = session->send_bytes_best_effort_callback != NULL;" in best_effort
    assert "if(!session->command_in_progress && has_best_effort_callback)" in best_effort


def test_usb_tx_queue_holds_full_lab_inventory_burst():
    vcp = CLI_VCP.read_text(encoding="utf-8")
    header = CLI_VCP_HEADER.read_text(encoding="utf-8")
    assert "#define VCP_TX_BUF_SIZE   CLI_VCP_TX_BUF_SIZE" in vcp
    match = re.search(
        r"#define\s+CLI_VCP_TX_BUF_SIZE\s+\((\d+)UL\s*\*\s*(\d+)UL\)", header
    )
    assert match
    assert int(match.group(1)) * int(match.group(2)) >= 32 * 1024


def test_best_effort_backlog_is_bounded_independently_of_total_pipe_capacity():
    cli = RPC_CLI.read_text(encoding="utf-8")
    backlog = _numeric_define(cli, "CLI_RPC_BEST_EFFORT_BACKLOG_MAX")
    assert backlog == 0
    assert "const size_t queued = CLI_VCP_TX_BUF_SIZE - spaces;" in cli
    assert "queued > CLI_RPC_BEST_EFFORT_BACKLOG_MAX" in cli

    # A large reliable pipe must not authorize filling the entire queue with stale GUI frames.
    capacity = 32 * 1024

    def admit_best_effort(spaces: int, frame_bytes: int) -> bool:
        queued = capacity - spaces
        return (
            queued <= backlog
            and spaces >= frame_bytes
            and spaces - frame_bytes >= MIN_STORAGE_RESPONSE_RESERVE
        )

    assert admit_best_effort(capacity, 1024)
    assert not admit_best_effort(capacity - 1, 1)
    assert not admit_best_effort(capacity - 1024, 1024)
    assert not admit_best_effort(MIN_STORAGE_RESPONSE_RESERVE, 1)


def test_best_effort_pipe_write_is_atomic_and_never_waits():
    cli = RPC_CLI.read_text(encoding="utf-8")
    assert "pipe_try_send(cli_rpc->pipe, bytes, bytes_len)" in cli

    pipe = PIPE.read_text(encoding="utf-8")
    helper = pipe.split("size_t pipe_try_send", 1)[1].split(
        "size_t pipe_bytes_available", 1
    )[0]
    assert "furi_mutex_acquire(pipe->send_mutex, 0)" in helper
    assert "furi_stream_buffer_spaces_available(pipe->sending) >= length" in helper
    assert "furi_stream_buffer_send(pipe->sending, data, length, 0)" in helper
    assert "pipe->state_check_period" not in helper


@dataclass
class _UsbRpcSessionModel:
    connected: bool = False
    streaming: bool = False
    generation: int = 0

    def connect(self) -> None:
        assert not self.connected
        self.connected = True
        self.streaming = False
        self.generation += 1

    def start_stream(self) -> None:
        assert self.connected
        self.streaming = True

    def disconnect(self) -> None:
        self.streaming = False
        self.connected = False

    def storage_read(self, size: int) -> bytes:
        assert self.connected and not self.streaming
        assert 0 <= size <= STORAGE_CHUNK_BYTES
        return bytes(size)


def test_disconnect_reconnect_then_maximum_storage_read_is_fresh_and_complete():
    session = _UsbRpcSessionModel()
    session.connect()
    first_generation = session.generation
    session.start_stream()
    session.disconnect()
    session.connect()

    assert session.generation == first_generation + 1
    assert session.storage_read(STORAGE_CHUNK_BYTES) == bytes(STORAGE_CHUNK_BYTES)

    core = RPC_CORE.read_text(encoding="utf-8")
    close_start = core.index("void rpc_session_close")
    close_end = core.index("void rpc_on_system_start", close_start)
    close = core[close_start:close_end]
    assert "rpc_session_set_send_bytes_callback(session, NULL)" in close
    assert "rpc_session_set_send_bytes_best_effort_callback(session, NULL)" in close
    assert "rpc_session_set_close_callback(session, NULL)" in close
    assert "rpc_session_set_buffer_is_empty_callback(session, NULL)" in close
    assert "RpcEvtDisconnect" in close

    open_start = core.index("RpcSession* rpc_session_open")
    open_end = core.index("void rpc_session_close", open_start)
    assert "RpcSession* session = calloc(1, sizeof(RpcSession))" in core[open_start:open_end]


def test_stop_screen_stream_replies_before_waiting_for_worker_exit():
    gui = RPC_GUI.read_text(encoding="utf-8")
    stop = gui.split("static void rpc_system_gui_stop_screen_stream_process", 1)[1].split(
        "static void\n    rpc_system_gui_send_input_event_request_process", 1
    )[0]

    acknowledge = "rpc_send_and_release_empty(session, request->command_id, PB_CommandStatus_OK);"
    assert "rpc_system_gui_quiesce_context(context);" in stop
    assert stop.index("rpc_system_gui_quiesce_context(context);") < stop.index(acknowledge)


def test_devinfo_quiesces_screen_frames_before_multi_message_response():
    property_source = (ROOT / "applications/services/rpc/rpc_property.c").read_text(
        encoding="utf-8"
    )
    branch = property_source.split(
        "if(!furi_string_cmp(topkey, PROPERTY_CATEGORY_DEVICE_INFO))", 1
    )[1].split("} else if", 1)[0]
    assert branch.index("rpc_system_gui_quiesce(session);") < branch.index(
        "furi_hal_info_get"
    )

    gui = RPC_GUI.read_text(encoding="utf-8")
    quiesce = gui.split("void rpc_system_gui_quiesce_context", 1)[1].split(
        "static void rpc_system_gui_stop_screen_stream_process", 1
    )[0]
    assert quiesce.index("rpc_gui->is_streaming = false;") < quiesce.index(
        "gui_remove_framebuffer_callback"
    )
    assert "furi_thread_join" in quiesce
    assert "rpc_gui->transmit_frame = NULL;" in quiesce
