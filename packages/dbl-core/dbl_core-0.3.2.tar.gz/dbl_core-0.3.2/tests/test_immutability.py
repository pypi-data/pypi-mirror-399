from dataclasses import FrozenInstanceError
from types import MappingProxyType

import pytest

from dbl_core import BehaviorV, DblEvent, DblEventKind


def test_immutability_event_and_behavior():
    event = DblEvent(DblEventKind.INTENT, correlation_id="c1", data={"a": 1})
    v = BehaviorV(events=(event,))

    # event dataclass is frozen
    with pytest.raises(FrozenInstanceError):
        event.correlation_id = "c2"  # type: ignore[misc]

    # data is deep-frozen (MappingProxyType for dicts)
    assert isinstance(event.data, (MappingProxyType, dict))  # defensive for future
    with pytest.raises(TypeError):
        event.data["a"] = 2  # type: ignore[index]

    # BehaviorV dataclass is frozen
    with pytest.raises(FrozenInstanceError):
        v.events = ()  # type: ignore[misc]

    # tuple inside is immutable too
    with pytest.raises(FrozenInstanceError):
        v.events += (event,)  # type: ignore[operator]
