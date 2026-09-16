#!/usr/bin/env python3
"""
MCP server: hallucination / citation confabulation detector.

Exposes:
  - detect_hallucination(answer, spans, ...)
  - audit_trace_budget(steps, spans, ...)

Supports two backends:
  - OpenAI API (default): Set OPENAI_API_KEY environment variable
  - Azure OpenAI pool: Set AOAI_POOL_JSON to path of pool config

Runs over STDIO for Claude Code.

IMPORTANT (stdio servers):
- Never print to stdout (it will corrupt JSON-RPC).
- Use logging (stderr) instead.
"""

from __future__ import annotations

import logging
import json
import math
import os
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# Ensure stderr logging only
logger = logging.getLogger("hallucination-detector-mcp")
logging.basicConfig(
    level=logging.INFO,
    stream=sys.stderr,
    format="[%(name)s] %(levelname)s: %(message)s",
)


# ----------------------------
# Minimal object types expected by strawberry.trace_budget
# ----------------------------
@dataclass
class Span:
    sid: str
    text: str


@dataclass
class Step:
    idx: int
    claim: str
    cites: List[str]
    confidence: float


@dataclass
class Trace:
    steps: List[Step]
    spans: List[Span]


# ----------------------------
# Helpers
# ----------------------------
_SENTENCE_SPLIT_RE = re.compile(r"(?<=[.!?])\s+")
# Citations like [S0], [S12], or [12].  This is deliberately the only pattern
# executed by the server: Python's stdlib regex engine has no match timeout, so
# compiling caller-controlled expressions would make the stdio process
# vulnerable to algorithmic-complexity denial of service (ReDoS).
_DEFAULT_CITE_PATTERN = r"\[(?P<id>[A-Za-z]\w*|\d+)\]"
_DEFAULT_CITE_RE = re.compile(_DEFAULT_CITE_PATTERN)

_LN2 = math.log(2.0)

MAX_ANSWER_CHARS = 65_536
MAX_SPANS = 256
MAX_SPAN_CHARS = 32_768
MAX_TOTAL_SPAN_CHARS = 262_144
MAX_STEPS = 256
MAX_CLAIM_CHARS = 65_536
MAX_CITES_PER_STEP = 128
MAX_IDENTIFIER_CHARS = 128
MAX_MODEL_CHARS = 128
MAX_PLACEHOLDER_CHARS = 512
MAX_CITATION_REGEX_CHARS = 512
MAX_POOL_CONFIG_BYTES = 1_048_576


def _bounded_text(value: Any, name: str, maximum: int, *, allow_empty: bool = False) -> str:
    if not isinstance(value, str):
        raise ValueError(f"{name} must be a string")
    value = value.strip()
    if not value and not allow_empty:
        raise ValueError(f"{name} must not be empty")
    if len(value) > maximum:
        raise ValueError(f"{name} exceeds {maximum} characters")
    return value


def _bounded_number(value: Any, name: str, minimum: float, maximum: float) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{name} must be a number")
    number = float(value)
    if not math.isfinite(number) or not minimum <= number <= maximum:
        raise ValueError(f"{name} must be between {minimum} and {maximum}")
    return number


def _bounded_integer(value: Any, name: str, minimum: int, maximum: int) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValueError(f"{name} must be an integer")
    if not minimum <= value <= maximum:
        raise ValueError(f"{name} must be between {minimum} and {maximum}")
    return value


def _validate_common_options(
    *,
    verifier_model: Any,
    default_target: Any,
    placeholder: Any,
    temperature: Any,
    top_logprobs: Any,
    max_concurrency: Any,
    timeout_s: Any,
    units: Any,
) -> Tuple[str, float, str, float, int, int, Optional[float], str]:
    model = _bounded_text(verifier_model, "verifier_model", MAX_MODEL_CHARS)
    target = _bounded_number(default_target, "default_target", 0.0, 1.0)
    replacement = _bounded_text(placeholder, "placeholder", MAX_PLACEHOLDER_CHARS)
    temp = _bounded_number(temperature, "temperature", 0.0, 2.0)
    logprobs = _bounded_integer(top_logprobs, "top_logprobs", 1, 20)
    concurrency = _bounded_integer(max_concurrency, "max_concurrency", 1, 32)
    if timeout_s is None:
        timeout = None
    else:
        timeout = _bounded_number(timeout_s, "timeout_s", 0.1, 300.0)
    if units not in {"bits", "nats"}:
        raise ValueError("units must be 'bits' or 'nats'")
    return model, target, replacement, temp, logprobs, concurrency, timeout, units


def _validate_pool_path(path: Optional[str]) -> Optional[str]:
    """Resolve a trusted startup-only AOAI pool file without following symlinks."""
    if path is None:
        return None
    raw = _bounded_text(path, "pool_json_path", 4096)
    candidate = Path(raw).expanduser()
    if candidate.is_symlink():
        raise ValueError("AOAI pool config must not be a symbolic link")
    resolved = candidate.resolve(strict=True)
    if not resolved.is_file():
        raise ValueError("AOAI pool config is not a regular file")
    if resolved.stat().st_size > MAX_POOL_CONFIG_BYTES:
        raise ValueError(f"AOAI pool config exceeds {MAX_POOL_CONFIG_BYTES} bytes")
    try:
        payload = json.loads(resolved.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise ValueError(f"AOAI pool config is not valid UTF-8 JSON: {error}") from error
    if not isinstance(payload, (dict, list)):
        raise ValueError("AOAI pool config must contain a JSON object or array")
    return str(resolved)


def _require_backend(pool_json_path: Optional[str]) -> None:
    if pool_json_path is None and not os.environ.get("OPENAI_API_KEY"):
        raise RuntimeError(
            "No verifier backend configured; set OPENAI_API_KEY or start the server "
            "with a validated AOAI_POOL_JSON file"
        )


def _compile_citation_regex(pattern: str) -> re.Pattern:
    """Return the precompiled canonical citation matcher.

    ``re`` cannot impose an execution deadline.  Pattern-shape filters are not
    a sound ReDoS defence because ambiguous alternation and other catastrophic
    forms have many spellings.  Keep the legacy argument for API compatibility,
    but never execute caller-controlled regex bytecode.
    """
    pattern = _bounded_text(pattern, "citation_regex", MAX_CITATION_REGEX_CHARS)
    if pattern != _DEFAULT_CITE_PATTERN:
        raise ValueError(
            "custom citation_regex execution is disabled for ReDoS safety; "
            "omit citation_regex or use the canonical pattern"
        )
    return _DEFAULT_CITE_RE


def _to_bits(nats: float) -> float:
    return float(nats) / _LN2


def _normalize_spans(spans: List[Dict[str, str]]) -> List[Span]:
    if not isinstance(spans, list):
        raise ValueError("spans must be an array")
    if len(spans) > MAX_SPANS:
        raise ValueError(f"spans exceeds {MAX_SPANS} entries")
    out: List[Span] = []
    total_chars = 0
    seen = set()
    for index, s in enumerate(spans):
        if not isinstance(s, dict):
            raise ValueError(f"spans[{index}] must be an object")
        if set(s) - {"sid", "text"}:
            raise ValueError(f"spans[{index}] contains unknown fields")
        sid = _bounded_text(s.get("sid"), f"spans[{index}].sid", MAX_IDENTIFIER_CHARS)
        text = _bounded_text(s.get("text"), f"spans[{index}].text", MAX_SPAN_CHARS)
        if sid in seen:
            raise ValueError(f"duplicate span id: {sid}")
        seen.add(sid)
        total_chars += len(text)
        if total_chars > MAX_TOTAL_SPAN_CHARS:
            raise ValueError(f"total span text exceeds {MAX_TOTAL_SPAN_CHARS} characters")
        out.append(Span(sid=sid, text=text))
    return out


def _normalize_steps(steps: List[Dict[str, Any]], default_target: float) -> List[Step]:
    if not isinstance(steps, list):
        raise ValueError("steps must be an array")
    if len(steps) > MAX_STEPS:
        raise ValueError(f"steps exceeds {MAX_STEPS} entries")
    out: List[Step] = []
    seen_indices = set()
    for i, st in enumerate(steps):
        if not isinstance(st, dict):
            raise ValueError(f"steps[{i}] must be an object")
        if set(st) - {"idx", "claim", "cites", "confidence"}:
            raise ValueError(f"steps[{i}] contains unknown fields")
        claim = _bounded_text(st.get("claim"), f"steps[{i}].claim", MAX_CLAIM_CHARS)
        idx = _bounded_integer(st.get("idx", i), f"steps[{i}].idx", 0, 1_000_000)
        if idx in seen_indices:
            raise ValueError(f"duplicate step idx: {idx}")
        seen_indices.add(idx)
        raw_cites = st.get("cites", [])
        if not isinstance(raw_cites, list) or len(raw_cites) > MAX_CITES_PER_STEP:
            raise ValueError(f"steps[{i}].cites must be an array with at most {MAX_CITES_PER_STEP} entries")
        cites = [_bounded_text(c, f"steps[{i}].cites", MAX_IDENTIFIER_CHARS) for c in raw_cites]
        conf = _bounded_number(st.get("confidence", default_target), f"steps[{i}].confidence", 0.0, 1.0)
        out.append(Step(idx=idx, claim=claim, cites=cites, confidence=conf))
    out.sort(key=lambda x: x.idx)
    return out


def _extract_cites(text: str, cite_re: re.Pattern) -> List[str]:
    return [m.group("id") for m in cite_re.finditer(text or "")]


def _split_claims(answer: str, mode: str, max_claims: int) -> List[str]:
    a = (answer or "").strip()
    if not a:
        return []

    if mode == "lines":
        raw = [ln.strip() for ln in a.splitlines() if ln.strip()]
    else:
        raw = [s.strip() for s in _SENTENCE_SPLIT_RE.split(a) if s.strip()]

    return raw[: max(1, int(max_claims))]


def _map_cites_to_known_ids(cites: List[str], known: set) -> List[str]:
    """
    Best-effort mapping so numeric cites can match either:
      - "12" (span id "12")
      - "S12" (span id "S12")
      - "S11" if caller uses 1-based in answer but spans are 0-based (common)
    """
    mapped: List[str] = []
    for c in cites:
        if c in known:
            mapped.append(c)
            continue

        if c.isdigit():
            n = int(c)
            if f"S{n}" in known:
                mapped.append(f"S{n}")
                continue
            if n > 0 and f"S{n-1}" in known:
                mapped.append(f"S{n-1}")
                continue

        if c.startswith("S") and c[1:].isdigit():
            tail = c[1:]
            if tail in known:
                mapped.append(tail)
                continue

        mapped.append(c)

    # de-dupe preserving order
    seen = set()
    out = []
    for c in mapped:
        if c not in seen:
            out.append(c)
            seen.add(c)
    return out


def _format_result(r, units: str) -> Dict[str, Any]:
    """Format a BudgetResult for JSON output."""
    if units == "bits":
        req_min = _to_bits(r.required_bits_min)
        req_max = _to_bits(r.required_bits_max)
        obs_min = _to_bits(r.observed_bits_min)
        obs_max = _to_bits(r.observed_bits_max)
        gap_min = _to_bits(r.budget_gap_min)
        gap_max = _to_bits(r.budget_gap_max)
    else:
        req_min, req_max = r.required_bits_min, r.required_bits_max
        obs_min, obs_max = r.observed_bits_min, r.observed_bits_max
        gap_min, gap_max = r.budget_gap_min, r.budget_gap_max

    return {
        "idx": r.idx,
        "claim": r.claim,
        "cites": r.cites,
        "target": r.target,
        "prior_yes": {
            "p_lower": r.prior_yes.p_yes_lower,
            "p_upper": r.prior_yes.p_yes_upper,
            "generated": r.prior_yes.generated,
            "topk": r.prior_yes.topk,
        },
        "post_yes": {
            "p_lower": r.post_yes.p_yes_lower,
            "p_upper": r.post_yes.p_yes_upper,
            "generated": r.post_yes.generated,
            "topk": r.post_yes.topk,
        },
        "required": {"min": req_min, "max": req_max, "units": units},
        "observed": {"min": obs_min, "max": obs_max, "units": units},
        "budget_gap": {"min": gap_min, "max": gap_max, "units": units},
        "flagged": bool(r.flagged),
        "has_any_citations": bool(r.cites),
    }


# ----------------------------
# Core detection logic
# ----------------------------

def run_detect_hallucination(
    answer: str,
    spans: List[Dict[str, str]],
    pool_json_path: Optional[str] = None,
    verifier_model: str = "gpt-4o-mini",
    default_target: float = 0.95,
    placeholder: str = "[REDACTED]",
    max_claims: int = 25,
    claim_split: str = "sentences",
    citation_regex: Optional[str] = None,
    temperature: float = 0.0,
    top_logprobs: int = 10,
    max_concurrency: int = 8,
    timeout_s: Optional[float] = 30.0,
    units: str = "bits",
) -> Dict[str, Any]:
    """
    Given a fully-written answer containing citations and the cited spans,
    compute an information-budget (scrub -> p0/p1 -> KL) diagnostic per claim.
    """
    answer = _bounded_text(answer, "answer", MAX_ANSWER_CHARS)
    if claim_split not in {"sentences", "lines"}:
        raise ValueError("claim_split must be 'sentences' or 'lines'")
    max_claims = _bounded_integer(max_claims, "max_claims", 1, MAX_STEPS)
    (
        verifier_model,
        default_target,
        placeholder,
        temperature,
        top_logprobs,
        max_concurrency,
        timeout_s,
        units,
    ) = _validate_common_options(
        verifier_model=verifier_model,
        default_target=default_target,
        placeholder=placeholder,
        temperature=temperature,
        top_logprobs=top_logprobs,
        max_concurrency=max_concurrency,
        timeout_s=timeout_s,
        units=units,
    )
    span_objs = _normalize_spans(spans)
    if not span_objs:
        return {
            "flagged": True,
            "under_budget": True,
            "error": "No spans provided (cannot verify citations).",
            "details": [],
        }

    if citation_regex is not None:
        cite_re = _compile_citation_regex(citation_regex)
    else:
        cite_re = _DEFAULT_CITE_RE
    known_ids = {s.sid for s in span_objs}
    claims = _split_claims(answer, mode=claim_split, max_claims=max_claims)

    steps: List[Step] = []
    for i, cl in enumerate(claims):
        cites = _extract_cites(cl, cite_re=cite_re)
        cites = _map_cites_to_known_ids(cites, known=known_ids)
        steps.append(Step(idx=i, claim=cl, cites=cites, confidence=float(default_target)))

    trace = Trace(steps=steps, spans=span_objs)
    _require_backend(pool_json_path)
    from .backend import BackendConfig
    from .trace_budget import score_trace_budget

    # Choose backend: aoai_pool if pool config provided, otherwise openai
    if pool_json_path:
        cfg = BackendConfig(
            kind="aoai_pool",
            aoai_pool_json_path=pool_json_path,
            max_concurrency=int(max_concurrency),
            timeout_s=timeout_s,
        )
        backend_name = "aoai_pool"
    else:
        cfg = BackendConfig(
            kind="openai",
            max_concurrency=int(max_concurrency),
            timeout_s=timeout_s,
        )
        backend_name = "openai"

    results = score_trace_budget(
        trace=trace,
        verifier_model=verifier_model,
        backend_cfg=cfg,
        default_target=float(default_target),
        temperature=float(temperature),
        top_logprobs=int(top_logprobs),
        placeholder=str(placeholder),
        reasoning=None,
    )

    details = [_format_result(r, units) for r in results]
    flagged = any(d["flagged"] for d in details)
    flagged_idxs = [d["idx"] for d in details if d["flagged"]]

    return {
        "flagged": flagged,
        "under_budget": flagged,
        "summary": {
            "claims_scored": len(details),
            "flagged_claims": len(flagged_idxs),
            "flagged_idxs": flagged_idxs[:50],
            "units": units,
            "verifier_model": verifier_model,
            "backend": backend_name,
        },
        "details": details,
    }


def run_audit_trace_budget(
    steps: List[Dict[str, Any]],
    spans: List[Dict[str, str]],
    pool_json_path: Optional[str] = None,
    verifier_model: str = "gpt-4o-mini",
    default_target: float = 0.95,
    placeholder: str = "[REDACTED]",
    temperature: float = 0.0,
    top_logprobs: int = 10,
    max_concurrency: int = 8,
    timeout_s: Optional[float] = 30.0,
    units: str = "bits",
) -> Dict[str, Any]:
    """
    Lower-level / more reliable entrypoint:
    provide already-atomic steps with explicit cite IDs, plus spans.
    """
    (
        verifier_model,
        default_target,
        placeholder,
        temperature,
        top_logprobs,
        max_concurrency,
        timeout_s,
        units,
    ) = _validate_common_options(
        verifier_model=verifier_model,
        default_target=default_target,
        placeholder=placeholder,
        temperature=temperature,
        top_logprobs=top_logprobs,
        max_concurrency=max_concurrency,
        timeout_s=timeout_s,
        units=units,
    )
    span_objs = _normalize_spans(spans)
    step_objs = _normalize_steps(steps, default_target=float(default_target))

    if not span_objs:
        return {
            "flagged": True,
            "under_budget": True,
            "error": "No spans provided (cannot verify citations).",
            "details": [],
        }
    if not step_objs:
        raise ValueError("steps must contain at least one claim")

    trace = Trace(steps=step_objs, spans=span_objs)
    _require_backend(pool_json_path)
    from .backend import BackendConfig
    from .trace_budget import score_trace_budget

    # Choose backend: aoai_pool if pool config provided, otherwise openai
    if pool_json_path:
        cfg = BackendConfig(
            kind="aoai_pool",
            aoai_pool_json_path=pool_json_path,
            max_concurrency=int(max_concurrency),
            timeout_s=timeout_s,
        )
        backend_name = "aoai_pool"
    else:
        cfg = BackendConfig(
            kind="openai",
            max_concurrency=int(max_concurrency),
            timeout_s=timeout_s,
        )
        backend_name = "openai"

    results = score_trace_budget(
        trace=trace,
        verifier_model=verifier_model,
        backend_cfg=cfg,
        default_target=float(default_target),
        temperature=float(temperature),
        top_logprobs=int(top_logprobs),
        placeholder=str(placeholder),
        reasoning=None,
    )

    out = []
    for r in results:
        if units == "bits":
            out.append({
                "idx": r.idx,
                "claim": r.claim,
                "cites": r.cites,
                "flagged": bool(r.flagged),
                "required": {"min": _to_bits(r.required_bits_min), "max": _to_bits(r.required_bits_max), "units": "bits"},
                "observed": {"min": _to_bits(r.observed_bits_min), "max": _to_bits(r.observed_bits_max), "units": "bits"},
                "budget_gap": {"min": _to_bits(r.budget_gap_min), "max": _to_bits(r.budget_gap_max), "units": "bits"},
            })
        else:
            out.append({
                "idx": r.idx,
                "claim": r.claim,
                "cites": r.cites,
                "flagged": bool(r.flagged),
                "required": {"min": r.required_bits_min, "max": r.required_bits_max, "units": "nats"},
                "observed": {"min": r.observed_bits_min, "max": r.observed_bits_max, "units": "nats"},
                "budget_gap": {"min": r.budget_gap_min, "max": r.budget_gap_max, "units": "nats"},
            })

    flagged = any(x["flagged"] for x in out)
    return {
        "flagged": flagged,
        "under_budget": flagged,
        "summary": {
            "steps_scored": len(out),
            "flagged_steps": sum(1 for x in out if x["flagged"]),
            "units": units,
            "verifier_model": verifier_model,
            "backend": backend_name,
        },
        "details": out,
    }


# ----------------------------
# MCP server setup
# ----------------------------

_COMMON_PROPERTIES = {
    "verifier_model": {"type": "string", "minLength": 1, "maxLength": MAX_MODEL_CHARS},
    "default_target": {"type": "number", "minimum": 0.0, "maximum": 1.0},
    "placeholder": {"type": "string", "minLength": 1, "maxLength": MAX_PLACEHOLDER_CHARS},
    "temperature": {"type": "number", "minimum": 0.0, "maximum": 2.0},
    "top_logprobs": {"type": "integer", "minimum": 1, "maximum": 20},
    "max_concurrency": {"type": "integer", "minimum": 1, "maximum": 32},
    "timeout_s": {
        "anyOf": [
            {"type": "number", "minimum": 0.1, "maximum": 300.0},
            {"type": "null"},
        ]
    },
    "units": {"type": "string", "enum": ["bits", "nats"]},
}
_SPAN_SCHEMA = {
    "type": "object",
    "properties": {
        "sid": {"type": "string", "minLength": 1, "maxLength": MAX_IDENTIFIER_CHARS},
        "text": {"type": "string", "minLength": 1, "maxLength": MAX_SPAN_CHARS},
    },
    "required": ["sid", "text"],
    "additionalProperties": False,
}
_TOOL_SCHEMAS = {
    "detect_hallucination": {
        "type": "object",
        "properties": {
            "answer": {"type": "string", "minLength": 1, "maxLength": MAX_ANSWER_CHARS},
            "spans": {"type": "array", "maxItems": MAX_SPANS, "items": _SPAN_SCHEMA},
            **_COMMON_PROPERTIES,
            "max_claims": {"type": "integer", "minimum": 1, "maximum": MAX_STEPS},
            "claim_split": {"type": "string", "enum": ["sentences", "lines"]},
            "citation_regex": {
                "type": "string",
                "enum": [_DEFAULT_CITE_PATTERN],
                "description": "Canonical citation pattern; arbitrary regex execution is disabled for ReDoS safety.",
            },
        },
        "required": ["answer", "spans"],
        "additionalProperties": False,
    },
    "audit_trace_budget": {
        "type": "object",
        "properties": {
            "steps": {
                "type": "array",
                "maxItems": MAX_STEPS,
                "items": {
                    "type": "object",
                    "properties": {
                        "idx": {"type": "integer", "minimum": 0, "maximum": 1_000_000},
                        "claim": {"type": "string", "minLength": 1, "maxLength": MAX_CLAIM_CHARS},
                        "cites": {
                            "type": "array",
                            "maxItems": MAX_CITES_PER_STEP,
                            "items": {"type": "string", "minLength": 1, "maxLength": MAX_IDENTIFIER_CHARS},
                        },
                        "confidence": {"type": "number", "minimum": 0.0, "maximum": 1.0},
                    },
                    "required": ["claim"],
                    "additionalProperties": False,
                },
            },
            "spans": {"type": "array", "maxItems": MAX_SPANS, "items": _SPAN_SCHEMA},
            **_COMMON_PROPERTIES,
        },
        "required": ["steps", "spans"],
        "additionalProperties": False,
    },
}


class _FallbackMCP:
    """Decorator-compatible adapter backed by the repository's stdio runtime."""

    def __init__(self) -> None:
        repo_root = Path(__file__).resolve().parents[4]
        runtime_dir = repo_root / ".ai" / "mcp" / "scripts"
        if str(runtime_dir) not in sys.path:
            sys.path.insert(0, str(runtime_dir))
        from mcp_stdio import MCPStdioServer

        self._server = MCPStdioServer("hallucination-detector", version="0.2.0")

    def tool(self):
        def register(handler):
            self._server.tool(
                handler.__name__,
                handler.__doc__ or handler.__name__,
                _TOOL_SCHEMAS[handler.__name__],
                handler,
            )
            return handler

        return register

    def run(self, **_kwargs) -> None:
        self._server.run()

def create_mcp_server(pool_json_path: Optional[str] = None):
    """Create and configure the MCP server.

    Args:
        pool_json_path: Optional path to Azure OpenAI pool config.
                       If None, uses standard OpenAI API with OPENAI_API_KEY.
    """
    pool_json_path = _validate_pool_path(pool_json_path)
    try:
        from mcp.server.fastmcp import FastMCP
    except ImportError:
        mcp = _FallbackMCP()
    else:
        mcp = FastMCP("hallucination-detector", json_response=True)

    @mcp.tool()
    def detect_hallucination(
        answer: str,
        spans: List[Dict[str, str]],
        verifier_model: str = "gpt-4o-mini",
        default_target: float = 0.95,
        placeholder: str = "[REDACTED]",
        max_claims: int = 25,
        claim_split: str = "sentences",
        citation_regex: Optional[str] = None,
        temperature: float = 0.0,
        top_logprobs: int = 10,
        max_concurrency: int = 8,
        timeout_s: Optional[float] = 30.0,
        units: str = "bits",
    ) -> Dict[str, Any]:
        """
        Given a fully-written answer containing citations and the cited spans,
        compute an information-budget (scrub -> p0/p1 -> KL) diagnostic per claim.

        Args:
            answer: The final answer text containing citations like [S0], [S1], etc.
            spans: List of {"sid": "S0", "text": "..."} objects for each cited span.
            verifier_model: Model to use for verification (e.g. gpt-4o-mini).
            default_target: Target confidence level (default 0.95).
            placeholder: Text to replace scrubbed citations with.
            max_claims: Maximum number of claims to process.
            claim_split: How to split answer into claims ("sentences" or "lines").
            citation_regex: Optional canonical citation pattern. Arbitrary custom
                regex execution is disabled because the stdlib engine has no
                match timeout.
            temperature: Sampling temperature for verifier.
            top_logprobs: Number of top logprobs to request.
            max_concurrency: Maximum concurrent requests.
            timeout_s: Timeout per request in seconds.
            units: Output units ("bits" or "nats").

        Returns:
            Dict with flagged status, summary, and per-claim details.
        """
        return run_detect_hallucination(
            answer=answer,
            spans=spans,
            pool_json_path=pool_json_path,
            verifier_model=verifier_model,
            default_target=default_target,
            placeholder=placeholder,
            max_claims=max_claims,
            claim_split=claim_split,
            citation_regex=citation_regex,
            temperature=temperature,
            top_logprobs=top_logprobs,
            max_concurrency=max_concurrency,
            timeout_s=timeout_s,
            units=units,
        )

    @mcp.tool()
    def audit_trace_budget(
        steps: List[Dict[str, Any]],
        spans: List[Dict[str, str]],
        verifier_model: str = "gpt-4o-mini",
        default_target: float = 0.95,
        placeholder: str = "[REDACTED]",
        temperature: float = 0.0,
        top_logprobs: int = 10,
        max_concurrency: int = 8,
        timeout_s: Optional[float] = 30.0,
        units: str = "bits",
    ) -> Dict[str, Any]:
        """
        Lower-level / more reliable entrypoint:
        provide already-atomic steps with explicit cite IDs, plus spans.

        Args:
            steps: List of {"idx": 0, "claim": "...", "cites": ["S0"], "confidence": 0.95}.
            spans: List of {"sid": "S0", "text": "..."} objects.
            verifier_model: Model to use for verification (e.g. gpt-4o-mini).
            default_target: Default confidence if not specified per-step.
            placeholder: Text to replace scrubbed citations with.
            temperature: Sampling temperature for verifier.
            top_logprobs: Number of top logprobs to request.
            max_concurrency: Maximum concurrent requests.
            timeout_s: Timeout per request in seconds.
            units: Output units ("bits" or "nats").

        Returns:
            Dict with flagged status, summary, and per-step details.
        """
        return run_audit_trace_budget(
            steps=steps,
            spans=spans,
            pool_json_path=pool_json_path,
            verifier_model=verifier_model,
            default_target=default_target,
            placeholder=placeholder,
            temperature=temperature,
            top_logprobs=top_logprobs,
            max_concurrency=max_concurrency,
            timeout_s=timeout_s,
            units=units,
        )

    return mcp


def main() -> None:
    """Entry point for the MCP server."""
    # Get pool config path from environment or command line (optional)
    pool_json_path = os.environ.get("AOAI_POOL_JSON")

    if len(sys.argv) > 2:
        logger.error("Usage: python -m strawberry.mcp_server [aoai-pool.json]")
        sys.exit(2)
    if not pool_json_path and len(sys.argv) == 2:
        pool_json_path = sys.argv[1]

    try:
        pool_json_path = _validate_pool_path(pool_json_path)
    except (OSError, ValueError) as error:
        logger.error("Invalid AOAI pool config: %s", error)
        sys.exit(2)

    if pool_json_path:
        logger.info("Starting hallucination-detector MCP server with Azure OpenAI pool")
    elif os.environ.get("OPENAI_API_KEY"):
        logger.info("Starting hallucination-detector MCP server with OpenAI API")
    else:
        logger.warning(
            "Starting without verifier credentials; initialize/tools/list remain available, "
            "and inference calls will return an explicit configuration error"
        )

    mcp = create_mcp_server(pool_json_path)
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
