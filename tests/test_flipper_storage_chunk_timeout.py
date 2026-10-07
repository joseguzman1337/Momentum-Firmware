from pathlib import Path

from scripts.flipper.storage import FlipperStorage


class RecordingRead:
    def __init__(self):
        self.calls = []

    def until(self, marker, cut_eol=True, timeout_sec=None):
        self.calls.append((marker, timeout_sec))
        return b"OK"


class RecordingPort:
    def __init__(self):
        self.writes = []

    def write(self, data):
        self.writes.append(data)
        return len(data)


def test_send_file_bounds_every_chunk_response_wait(tmp_path, monkeypatch):
    monkeypatch.setenv("FBT_STORAGE_CHUNK_RESPONSE_TIMEOUT", "17")
    monkeypatch.setenv("FBT_STORAGE_RESUME_STATE_DIR", str(tmp_path / "state"))
    source = tmp_path / "payload.bin"
    source.write_bytes(b"payload")
    storage = FlipperStorage.__new__(FlipperStorage)
    storage.chunk_size = 4096
    storage.port = RecordingPort()
    storage.read = RecordingRead()
    storage.exist_file = lambda _path: False
    storage.send_and_wait_eol = lambda _command: None
    storage.has_error = lambda _answer: False

    storage.send_file(str(source), "/ext/payload.bin")

    assert storage.read.calls == [
        (storage.CLI_EOL, 17.0),
        (storage.CLI_PROMPT, 17.0),
    ]


def test_send_file_resumes_an_incomplete_remote_file(tmp_path, monkeypatch):
    monkeypatch.setenv("FBT_STORAGE_RESUME", "1")
    state_dir = tmp_path / "state"
    monkeypatch.setenv("FBT_STORAGE_RESUME_STATE_DIR", str(state_dir))
    source = tmp_path / "payload.bin"
    source.write_bytes(b"0123456789")
    storage = FlipperStorage.__new__(FlipperStorage)
    storage.chunk_size = 4
    storage.port = RecordingPort()
    storage.read = RecordingRead()
    storage.exist_file = lambda _path: True
    storage.size = lambda _path: 6
    storage.remove = lambda _path: (_ for _ in ()).throw(
        AssertionError("partial remote file must be preserved")
    )
    commands = []
    storage.send_and_wait_eol = commands.append
    storage.has_error = lambda _answer: False

    identity = {"sha256": __import__("hashlib").sha256(b"0123456789").hexdigest(), "size": 10}
    state_dir.mkdir()
    state_name = __import__("hashlib").sha256(b"/ext/payload.bin").hexdigest() + ".json"
    (state_dir / state_name).write_text(__import__("json").dumps(identity))

    storage.send_file(str(source), "/ext/payload.bin")

    assert commands == ['storage write_chunk "/ext/payload.bin" 4\r']
    assert storage.port.writes == [b"6789"]


def test_send_file_restarts_when_local_identity_changed(tmp_path, monkeypatch):
    monkeypatch.setenv("FBT_STORAGE_RESUME", "1")
    monkeypatch.setenv("FBT_STORAGE_RESUME_STATE_DIR", str(tmp_path / "state"))
    source = tmp_path / "payload.bin"
    source.write_bytes(b"new-content")
    storage = FlipperStorage.__new__(FlipperStorage)
    storage.chunk_size = 32
    storage.port = RecordingPort()
    storage.read = RecordingRead()
    storage.exist_file = lambda _path: True
    storage.size = lambda _path: 4
    removed = []
    storage.remove = removed.append
    storage.send_and_wait_eol = lambda _command: None
    storage.has_error = lambda _answer: False

    storage.send_file(str(source), "/ext/payload.bin")

    assert removed == ["/ext/payload.bin"]
    assert storage.port.writes == [b"new-content"]
