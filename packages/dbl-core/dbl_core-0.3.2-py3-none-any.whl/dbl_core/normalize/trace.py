from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from kl_kernel_logic import ExecutionTrace  # type: ignore[import-untyped]

from ..events.canonical import canonicalize_value
from ..events.errors import InvalidTraceError
from ..events.trace_digest import trace_digest

OBSERVATIONAL_TRACE_KEYS: frozenset[str] = frozenset(
    {
        "runtime_ms",
        "duration_ms",
        "latency_ms",
        "timing_ms",
        "perf_ms",
        "runtime_ns",
        "duration_ns",
        "latency_ns",
    }
)


def sanitize_trace(value: Any) -> Any:
    if isinstance(value, Mapping):
        cleaned: dict[str, Any] = {}
        for key, item in value.items():
            if not isinstance(key, str):
                raise InvalidTraceError(f"mapping key must be str, got: {type(key).__name__}")
            if key in OBSERVATIONAL_TRACE_KEYS:
                continue
            cleaned[key] = sanitize_trace(item)
        return cleaned
    if isinstance(value, list):
        return [sanitize_trace(v) for v in value]
    if isinstance(value, tuple):
        return [sanitize_trace(v) for v in value]
    return value


def normalize_trace(trace: ExecutionTrace | Mapping[str, Any]) -> tuple[dict[str, Any], str]:
    """Normalize a kernel trace or a raw trace mapping with a provided trace_digest."""
    if isinstance(trace, ExecutionTrace):
        raw = trace.to_dict(include_observational=True)
        if not isinstance(raw, Mapping):
            raise InvalidTraceError("ExecutionTrace.to_dict() must produce a Mapping")
        sanitized_raw = sanitize_trace(raw)
        try:
            trace_any = canonicalize_value(sanitized_raw)
        except Exception as exc:
            raise InvalidTraceError(str(exc)) from exc
        if not isinstance(trace_any, Mapping):
            raise InvalidTraceError("ExecutionTrace.to_dict() must produce a Mapping")
        trace_dict = dict(trace_any)
        return trace_dict, trace_digest(trace_dict)

    if isinstance(trace, Mapping):
        provided_digest = trace.get("trace_digest")
        if not isinstance(provided_digest, str) or not provided_digest:
            raise InvalidTraceError("trace_digest is required when providing raw trace dict")

        trace_copy = dict(trace)
        trace_copy.pop("trace_digest", None)
        try:
            trace_any = canonicalize_value(trace_copy)
        except Exception as exc:
            raise InvalidTraceError(str(exc)) from exc
        if not isinstance(trace_any, Mapping):
            raise InvalidTraceError("trace must canonicalize to a Mapping")
        trace_dict = dict(trace_any)
        return trace_dict, provided_digest

    raise InvalidTraceError("trace must be ExecutionTrace or Mapping")
