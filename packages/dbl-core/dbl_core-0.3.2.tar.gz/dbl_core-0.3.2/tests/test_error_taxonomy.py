import pytest

from dbl_core import DblEvent, DblEventKind, normalize_trace
from dbl_core.events.errors import InvalidEventError, InvalidTraceError


def test_invalid_event_payload_raises_invalid_event_error():
    with pytest.raises(InvalidEventError, match="non-serializable type"):
        DblEvent(DblEventKind.INTENT, correlation_id="c1", data={"bad": object()})


def test_trace_digest_mismatch_raises_invalid_trace_error():
    data = {"trace": {"a": 1}, "trace_digest": "bad"}
    with pytest.raises(InvalidTraceError, match="trace_digest mismatch"):
        DblEvent(DblEventKind.EXECUTION, correlation_id="c1", data=data)


def test_raw_trace_missing_digest_raises_invalid_trace_error():
    with pytest.raises(InvalidTraceError, match="trace_digest is required"):
        normalize_trace({"trace": {"a": 1}})
