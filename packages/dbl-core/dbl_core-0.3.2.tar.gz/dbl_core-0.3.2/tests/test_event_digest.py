import pytest

from dbl_core import DblEvent, DblEventKind
from dbl_core.events.errors import InvalidTraceError
from dbl_core.events.trace_digest import trace_digest


def test_event_digest_stability():
    event_a = DblEvent(
        DblEventKind.INTENT,
        correlation_id="c1",
        data={"psi": "x"},
        observational={"note": "one"},
    )
    event_b = DblEvent(
        DblEventKind.INTENT,
        correlation_id="c1",
        data={"psi": "x"},
        observational={"note": "two"},
    )
    assert event_a.digest() == event_b.digest()


def test_execution_event_wrong_trace_digest_raises():
    data = {
        "trace": {"a": 1},
        "trace_digest": "bad",
    }
    with pytest.raises(InvalidTraceError, match="trace_digest mismatch"):
        DblEvent(DblEventKind.EXECUTION, correlation_id="c1", data=data)


def test_execution_event_trace_digest_matches_full_trace():
    trace = {"a": 1, "b": {"c": 2}}
    data = {"trace": trace, "trace_digest": trace_digest(trace)}
    e = DblEvent(DblEventKind.EXECUTION, correlation_id="c1", data=data)
    assert e.digest() == e.digest()
