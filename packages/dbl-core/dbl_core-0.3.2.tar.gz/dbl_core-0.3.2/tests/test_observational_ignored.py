from dbl_core import DblEvent, DblEventKind
from dbl_core.events.trace_digest import trace_digest


def test_observational_ignored_in_digest():
    trace = {"a": 1}
    base = {"trace": trace, "trace_digest": trace_digest(trace)}

    event_a = DblEvent(
        DblEventKind.EXECUTION,
        correlation_id="c1",
        data=base,
        observational={"note": "one"},
    )
    event_b = DblEvent(
        DblEventKind.EXECUTION,
        correlation_id="c1",
        data=base,
        observational={"note": "two"},
    )

    assert event_a.digest() == event_b.digest()
