from dbl_core import BehaviorV, DblEvent, DblEventKind


def test_deterministic_replay_digest_ignores_observational():
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

    behavior_a = BehaviorV(events=(event_a,))
    behavior_b = BehaviorV(events=(event_b,))

    assert event_a.digest() == event_b.digest()
    assert behavior_a.digest() == behavior_b.digest()
