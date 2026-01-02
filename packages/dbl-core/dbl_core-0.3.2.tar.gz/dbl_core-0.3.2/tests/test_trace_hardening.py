import pytest

from dbl_core import normalize_trace
from dbl_core.events.errors import InvalidTraceError


def test_normalize_trace_rejects_non_str_keys():
    with pytest.raises(InvalidTraceError, match="mapping key must be str"):
        normalize_trace({1: "x", "trace_digest": "deadbeef"})  # type: ignore[dict-item]
