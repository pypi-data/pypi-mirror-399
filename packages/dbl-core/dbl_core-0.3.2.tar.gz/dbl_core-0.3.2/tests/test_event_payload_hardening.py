import pytest

from dbl_core import DblEvent, DblEventKind
from dbl_core.events.errors import InvalidEventError


def test_event_data_mapping_key_must_be_str():
    with pytest.raises(InvalidEventError, match="mapping key must be str"):
        DblEvent(DblEventKind.INTENT, correlation_id="c1", data={1: "x"})  # type: ignore[dict-item]


def test_event_observational_mapping_key_must_be_str():
    with pytest.raises(InvalidEventError, match="mapping key must be str"):
        DblEvent(
            DblEventKind.INTENT,
            correlation_id="c1",
            data={"ok": 1},
            observational={1: "x"},  # type: ignore[dict-item]
        )


def test_event_data_float_is_rejected():
    with pytest.raises(InvalidEventError, match="float is not allowed"):
        DblEvent(DblEventKind.INTENT, correlation_id="c1", data={"x": 0.1})


def test_event_data_set_must_be_primitive_only():
    with pytest.raises(InvalidEventError, match="set values must be JSON primitives"):
        DblEvent(DblEventKind.INTENT, correlation_id="c1", data={"s": {("x",)}})
