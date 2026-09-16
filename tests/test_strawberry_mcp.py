import importlib
import json
import os
from pathlib import Path
import subprocess
import sys

import pytest


REPO_ROOT = Path(__file__).resolve().parents[1]
STRAWBERRY_SRC = REPO_ROOT / ".ai" / "strawberry" / "src"


@pytest.fixture()
def strawberry_mcp(monkeypatch):
    monkeypatch.syspath_prepend(str(STRAWBERRY_SRC))
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("AOAI_POOL_JSON", raising=False)
    sys.modules.pop("strawberry.mcp_server", None)
    return importlib.import_module("strawberry.mcp_server")


def _run_protocol(requests):
    env = os.environ.copy()
    env.pop("OPENAI_API_KEY", None)
    env.pop("AOAI_POOL_JSON", None)
    env["PYTHONPATH"] = str(STRAWBERRY_SRC)
    payload = "".join(json.dumps(request) + "\n" for request in requests)
    return subprocess.run(
        [sys.executable, "-S", "-m", "strawberry.mcp_server"],
        input=payload,
        text=True,
        capture_output=True,
        env=env,
        cwd=REPO_ROOT,
        timeout=5,
        check=False,
    )


def test_dependency_free_server_initializes_and_lists_tools_without_credentials():
    result = _run_protocol(
        [
            {"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}},
            {"jsonrpc": "2.0", "method": "notifications/initialized"},
            {"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}},
        ]
    )
    assert result.returncode == 0, result.stderr
    responses = [json.loads(line) for line in result.stdout.splitlines()]
    assert [response["id"] for response in responses] == [1, 2]
    assert responses[0]["result"]["serverInfo"]["name"] == "hallucination-detector"
    tools = responses[1]["result"]["tools"]
    assert {tool["name"] for tool in tools} == {
        "detect_hallucination",
        "audit_trace_budget",
    }
    assert all(tool["inputSchema"]["additionalProperties"] is False for tool in tools)


def test_missing_backend_is_reported_honestly_without_inference_call():
    result = _run_protocol(
        [
            {
                "jsonrpc": "2.0",
                "id": 3,
                "method": "tools/call",
                "params": {
                    "name": "detect_hallucination",
                    "arguments": {
                        "answer": "A claim [S0].",
                        "spans": [{"sid": "S0", "text": "Evidence."}],
                    },
                },
            }
        ]
    )
    assert result.returncode == 0
    response = json.loads(result.stdout)
    assert response["result"]["isError"] is True
    assert "No verifier backend configured" in response["result"]["content"][0]["text"]


@pytest.mark.parametrize(
    "kwargs, message",
    [
        ({"answer": "x", "spans": "bad"}, "spans must be an array"),
        ({"answer": "x", "spans": [{"sid": "S0", "text": "a"}, {"sid": "S0", "text": "b"}]}, "duplicate span id"),
        ({"answer": "x", "spans": [{"sid": "S0", "text": "a"}], "units": "bytes"}, "units must be"),
        ({"answer": "x", "spans": [{"sid": "S0", "text": "a"}], "citation_regex": "(x)"}, "disabled for ReDoS safety"),
        ({"answer": "x", "spans": [{"sid": "S0", "text": "a"}], "citation_regex": "(?P<id>(a|aa)+)"}, "disabled for ReDoS safety"),
    ],
)
def test_detect_rejects_invalid_or_unbounded_inputs_before_backend(strawberry_mcp, kwargs, message):
    with pytest.raises(ValueError, match=message):
        strawberry_mcp.run_detect_hallucination(**kwargs)


def test_adversarial_ambiguous_regex_is_rejected_without_scanning_input(strawberry_mcp):
    # If this caller-controlled expression were compiled and searched, the
    # non-matching suffix could trigger exponential backtracking.
    adversarial_pattern = r"(?P<id>(a|aa)+)$"
    adversarial_answer = "a" * 65_000 + "!"
    with pytest.raises(ValueError, match="disabled for ReDoS safety"):
        strawberry_mcp.run_detect_hallucination(
            answer=adversarial_answer,
            spans=[{"sid": "S0", "text": "evidence"}],
            citation_regex=adversarial_pattern,
        )


def test_canonical_citation_pattern_reuses_precompiled_matcher(strawberry_mcp):
    assert strawberry_mcp._compile_citation_regex(strawberry_mcp._DEFAULT_CITE_PATTERN) is strawberry_mcp._DEFAULT_CITE_RE


def test_pool_path_rejects_symlink_and_invalid_json(strawberry_mcp, tmp_path):
    invalid = tmp_path / "pool.json"
    invalid.write_text("not json", encoding="utf-8")
    with pytest.raises(ValueError, match="valid UTF-8 JSON"):
        strawberry_mcp._validate_pool_path(str(invalid))

    real = tmp_path / "real.json"
    real.write_text("{}", encoding="utf-8")
    link = tmp_path / "link.json"
    link.symlink_to(real)
    with pytest.raises(ValueError, match="symbolic link"):
        strawberry_mcp._validate_pool_path(str(link))


def test_empty_spans_returns_explicit_unverifiable_result_without_backend(strawberry_mcp):
    result = strawberry_mcp.run_detect_hallucination(answer="A claim.", spans=[])
    assert result["flagged"] is True
    assert "cannot verify" in result["error"]
