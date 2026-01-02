from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from .canonical import canonicalize_value, digest_bytes, json_dumps


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
