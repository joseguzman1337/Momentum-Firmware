from pathlib import Path
import re


SOURCE = Path("targets/f7/furi_hal/furi_hal_usb_eth.c")


def test_usb_eth_preserves_three_independent_2048_byte_buffers():
    source = SOURCE.read_text()

    assert "#define ETH_FRAME_BUFFER_SIZE 2048" in source
    for member in ("tx", "rx_worker", "rx_isr"):
        assert re.search(rf"uint8_t\s+{member}\[ETH_FRAME_BUFFER_SIZE\]", source)
    assert "malloc(sizeof(EthFrameBuffers))" in source


def test_usb_eth_buffers_follow_interface_lifecycle():
    source = SOURCE.read_text()
    init = source.index("static void eth_init(")
    allocation = source.index("eth_frame_buffers = malloc(sizeof(EthFrameBuffers));", init)
    thread_start = source.index("furi_thread_start(eth_rx_thread);", init)
    deinit = source.index("static void eth_deinit(", thread_start)
    release = source.index("free(eth_frame_buffers);", deinit)
    clear = source.index("eth_frame_buffers = NULL;", release)

    assert init < allocation < thread_start < deinit < release < clear


def test_usb_eth_has_no_always_resident_function_static_frame_buffers():
    source = SOURCE.read_text()

    assert not re.search(r"static\s+uint8_t\s+\w+\s*\[\s*2048\s*\]", source)
