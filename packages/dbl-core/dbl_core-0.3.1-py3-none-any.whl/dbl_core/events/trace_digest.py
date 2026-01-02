from __future__ import annotations

from typing import Any, Mapping

from .canonical import canonicalize_value, json_dumps, digest_bytes


def trace_digest(trace_dict: Mapping[str, Any]) -> str:
    """
    Canonical integrity digest for a trace artifact.

    Contract:
    - This is not domain semantics.
    - It is sha256 over canonical JSON bytes of the fully canonicalized trace mapping.
    """
    canonical = canonicalize_value(trace_dict)
    if not isinstance(canonical, Mapping):
        raise TypeError("trace must canonicalize to a Mapping")
    return digest_bytes(json_dumps(canonical))
