from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, ClassVar

from ..gate.model import GateDecision
from ..normalize.trace import sanitize_trace
from .canonical import canonicalize_value, digest_bytes, freeze_value, json_dumps
from .errors import InvalidEventError, InvalidTraceError
from .trace_digest import trace_digest


class DblEventKind(str, Enum):
    INTENT = "INTENT"
    DECISION = "DECISION"
    EXECUTION = "EXECUTION"
    PROOF = "PROOF"


@dataclass(frozen=True)
class DblEvent:
    event_kind: DblEventKind
    correlation_id: str
    data: Any = field(default_factory=dict)
    observational: Mapping[str, Any] | None = None

    DETERMINISTIC_FIELDS: ClassVar[tuple[str, ...]] = (
        "event_kind",
        "correlation_id",
        "data",
    )
    OBSERVATIONAL_FIELDS: ClassVar[tuple[str, ...]] = ("observational",)

    def __post_init__(self) -> None:
        if not isinstance(self.correlation_id, str) or not self.correlation_id:
            raise InvalidEventError("correlation_id must be a non-empty string")

        if isinstance(self.data, GateDecision):
            try:
                canonicalize_value(self.data.to_dict(include_observational=True))
            except Exception as exc:
                raise InvalidEventError(str(exc)) from exc
        elif self.data is not None:
            try:
                canonicalize_value(self.data)
            except Exception as exc:
                raise InvalidEventError(str(exc)) from exc
        if self.observational is not None:
            try:
                canonicalize_value(self.observational)
            except Exception as exc:
                raise InvalidEventError(str(exc)) from exc

        if self.event_kind == DblEventKind.DECISION:
            if isinstance(self.data, Mapping):
                if len(self.data) == 0:
                    raise InvalidEventError("DECISION event data must be non-empty")
            elif isinstance(self.data, GateDecision):
                pass
            else:
                raise InvalidEventError("DECISION event data must be a Mapping or GateDecision")

        if self.event_kind == DblEventKind.EXECUTION:
            if not isinstance(self.data, Mapping):
                raise InvalidEventError("EXECUTION event data must be a Mapping")
            if (
                "trace_digest" not in self.data
                or not isinstance(self.data["trace_digest"], str)
                or not self.data["trace_digest"]
            ):
                raise InvalidTraceError("EXECUTION event data requires trace_digest: non-empty str")
            if "trace" not in self.data or not isinstance(self.data["trace"], Mapping):
                raise InvalidTraceError("EXECUTION event data requires trace: Mapping")

            trace = self.data["trace"]
            try:
                sanitized = sanitize_trace(trace)
                actual = trace_digest(sanitized)
            except Exception as exc:
                raise InvalidTraceError(str(exc)) from exc

            if actual != self.data["trace_digest"]:
                raise InvalidTraceError("EXECUTION event trace_digest mismatch")

        object.__setattr__(self, "data", freeze_value(self.data))
        if self.observational is not None:
            object.__setattr__(self, "observational", freeze_value(self.observational))

    def _data_for_dict(self, *, include_observational: bool) -> Any:
        if isinstance(self.data, GateDecision):
            return self.data.to_dict(include_observational=include_observational)

        if isinstance(self.data, Mapping):
            data = canonicalize_value(self.data)
            if (
                self.event_kind == DblEventKind.EXECUTION
                and not include_observational
                and isinstance(data, Mapping)
                and "trace" in data
            ):
                filtered = dict(data)
                filtered.pop("trace", None)
                return filtered
            return data

        return canonicalize_value(self.data)

    def to_dict(self, *, include_observational: bool = True) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "event_kind": self.event_kind.value,
            "correlation_id": self.correlation_id,
            "data": self._data_for_dict(include_observational=include_observational),
        }
        if include_observational and self.observational is not None:
            payload["observational"] = canonicalize_value(self.observational)
        return payload

    def to_json(self, *, include_observational: bool = True) -> str:
        return json_dumps(self.to_dict(include_observational=include_observational))

    def digest(self) -> str:
        return digest_bytes(self.to_json(include_observational=False))
