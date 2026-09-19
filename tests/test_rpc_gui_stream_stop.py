from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "applications/services/rpc/rpc_gui.c"


def test_stop_stream_removes_callback_before_stopping_worker_and_acknowledging():
    source = SOURCE.read_text(encoding="utf-8")
    start = source.index("static void rpc_system_gui_stop_screen_stream_process")
    end = source.index("static void\n    rpc_system_gui_send_input_event_request_process", start)
    handler = source[start:end]
    exit_signal = handler.index("RpcGuiWorkerFlagExit")
    acknowledgement = handler.index("rpc_send_and_release_empty")
    remove_callback = handler.index("gui_remove_framebuffer_callback")
    join = handler.index("furi_thread_join")
    assert remove_callback < exit_signal < acknowledgement < join
    assert "return;" in handler[join:]


def test_best_effort_frames_reserve_pipe_space_for_control_replies():
    source = (ROOT / "applications/services/rpc/rpc_cli.c").read_text(encoding="utf-8")
    assert "#define CLI_RPC_STORAGE_RESPONSE_MAX 768UL" in source
    assert "#define CLI_RPC_CONTROL_RESERVE CLI_RPC_STORAGE_RESPONSE_MAX" in source
    assert "(spaces - bytes_len) < CLI_RPC_CONTROL_RESERVE" in source


def test_session_cleanup_removes_callback_before_stopping_worker():
    source = SOURCE.read_text(encoding="utf-8")
    start = source.index("void rpc_system_gui_free")
    cleanup = source[start:]
    assert cleanup.index("gui_remove_framebuffer_callback") < cleanup.index("RpcGuiWorkerFlagExit")
    assert cleanup.index("RpcGuiWorkerFlagExit") < cleanup.index("furi_thread_join")


def test_framebuffer_callback_never_waits_for_transport():
    source = SOURCE.read_text(encoding="utf-8")
    start = source.index("static void rpc_system_gui_screen_stream_frame_callback")
    end = source.index("static int32_t rpc_system_gui_screen_stream_frame_transmit_thread", start)
    callback = source[start:end]
    assert "furi_mutex_acquire(rpc_gui->transmit_mutex, 0)" in callback
    assert "FuriWaitForever" not in callback


def test_stream_worker_prioritizes_exit_and_frame_is_zero_initialized():
    source = SOURCE.read_text(encoding="utf-8")
    worker_start = source.index("rpc_system_gui_screen_stream_frame_transmit_thread")
    worker_end = source.index("rpc_system_gui_start_screen_stream_process", worker_start)
    worker = source[worker_start:worker_end]
    assert worker.index("if(flags & RpcGuiWorkerFlagExit)") < worker.index(
        "if(flags & RpcGuiWorkerFlagTransmit)"
    )
    assert "(PB_Main)PB_Main_init_zero" in source
    assert "rpc_send_best_effort(rpc_gui->session, rpc_gui->transmit_frame)" in worker
