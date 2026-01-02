from __future__ import annotations

from typing import Any, Mapping, Tuple

from kl_kernel_logic import ExecutionTrace

from ..events.canonical import canonicalize_value
from ..events.trace_digest import trace_digest


_OBSERVATIONAL_FLOAT_KEYS = {
    "runtime_ms",
    "duration_ms",
    "latency_ms",
    "timing_ms",
    "perf_ms",
    "runtime_ns",
    "duration_ns",
    "latency_ns",
}


def _strip_observational_keys(value: Any) -> Any:
    if isinstance(value, Mapping):
        cleaned: dict[str, Any] = {}
        for key, item in value.items():
            if not isinstance(key, str):
                raise TypeError(f"mapping key must be str, got: {type(key).__name__}")
            if key in _OBSERVATIONAL_FLOAT_KEYS:
                continue
            cleaned[key] = _strip_observational_keys(item)
        return cleaned
    if isinstance(value, list):
        return [_strip_observational_keys(v) for v in value]
    if isinstance(value, tuple):
        return [_strip_observational_keys(v) for v in value]
    return value


def normalize_trace(trace: ExecutionTrace | Mapping[str, Any]) -> Tuple[dict[str, Any], str]:
    """Normalize a kernel trace or a raw trace mapping with a provided trace_digest."""
    if isinstance(trace, ExecutionTrace):
        raw = trace.to_dict(include_observational=True)
        if not isinstance(raw, Mapping):
            raise TypeError("ExecutionTrace.to_dict() must produce a Mapping")
        sanitized_raw = _strip_observational_keys(raw)
        trace_any = canonicalize_value(sanitized_raw)
        if not isinstance(trace_any, Mapping):
            raise TypeError("ExecutionTrace.to_dict() must produce a Mapping")
        trace_dict = dict(trace_any)
        return trace_dict, trace_digest(trace_dict)

    if isinstance(trace, Mapping):
        trace_any = canonicalize_value(trace)
        if not isinstance(trace_any, Mapping):
            raise TypeError("trace must canonicalize to a Mapping")
        trace_dict = dict(trace_any)

        provided_digest = trace.get("trace_digest")
        if not isinstance(provided_digest, str) or not provided_digest:
            raise ValueError("trace_digest is required when providing raw trace dict")
        return trace_dict, provided_digest

    raise TypeError("trace must be ExecutionTrace or Mapping")
