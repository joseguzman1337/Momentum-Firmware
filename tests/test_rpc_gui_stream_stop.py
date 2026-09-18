from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "applications/services/rpc/rpc_gui.c"


def test_stop_stream_acknowledges_before_joining_worker():
    source = SOURCE.read_text(encoding="utf-8")
    start = source.index("static void rpc_system_gui_stop_screen_stream_process")
    end = source.index("static void\n    rpc_system_gui_send_input_event_request_process", start)
    handler = source[start:end]
    exit_signal = handler.index("RpcGuiWorkerFlagExit")
    acknowledgement = handler.index("rpc_send_and_release_empty")
    join = handler.index("furi_thread_join")
    assert exit_signal < acknowledgement < join
    assert "return;" in handler[join:]


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
