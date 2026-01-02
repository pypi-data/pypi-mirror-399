from __future__ import annotations

import json
from collections.abc import Mapping
from datetime import UTC, datetime
from hashlib import sha256
from types import MappingProxyType
from typing import Any

_PRIMITIVE = (str, int, bool)


def _is_primitive_set_value(v: Any) -> bool:
    return isinstance(v, _PRIMITIVE) or v is None


def _set_sort_key(v: Any) -> tuple[str, Any]:
    if v is None:
        return ("null", "")
    if isinstance(v, bool):
        return ("bool", v)
    if isinstance(v, int):
        return ("int", v)
    if isinstance(v, str):
        return ("str", v)
    raise TypeError(f"set contains non-primitive value: {type(v).__name__}")


def freeze_value(value: Any) -> Any:
    if isinstance(value, Mapping):
        return MappingProxyType({k: freeze_value(v) for k, v in value.items()})
    if isinstance(value, tuple):
        return tuple(freeze_value(v) for v in value)
    if isinstance(value, list):
        return tuple(freeze_value(v) for v in value)
    if isinstance(value, set):
        return frozenset(freeze_value(v) for v in value)
    return value


def format_dt(value: datetime) -> str:
    if value.tzinfo is None:
        value = value.replace(tzinfo=UTC)
    return value.astimezone(UTC).isoformat().replace("+00:00", "Z")


def canonicalize_value(value: Any) -> Any:
    if isinstance(value, datetime):
        return format_dt(value)

    if isinstance(value, Mapping):
        items: dict[str, Any] = {}
        for key in sorted(value.keys()):
            if not isinstance(key, str):
                raise TypeError(f"mapping key must be str, got: {type(key).__name__}")
            items[key] = canonicalize_value(value[key])
        return items

    if isinstance(value, (list, tuple)):
        return [canonicalize_value(v) for v in value]

    if isinstance(value, set):
        if not all(_is_primitive_set_value(v) for v in value):
            raise TypeError("set values must be JSON primitives (str, int, bool, None)")
        normalized = [canonicalize_value(v) for v in value]
        return sorted(normalized, key=_set_sort_key)

    if isinstance(value, float):
        raise TypeError("float is not allowed in canonicalized values")

    if isinstance(value, (str, int, bool)) or value is None:
        return value

    raise TypeError(f"non-serializable type in canonicalization: {type(value).__name__}")


def json_dumps(data: Any) -> str:
    return json.dumps(
        data,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
        allow_nan=False,
    )


def digest_bytes(payload: str) -> str:
    return sha256(payload.encode("utf-8")).hexdigest()
