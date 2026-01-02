import pytest

from dbl_core import normalize_trace


def test_normalize_trace_rejects_non_str_keys():
    with pytest.raises(TypeError, match="mapping key must be str"):
        normalize_trace({1: "x"})  # type: ignore[dict-item]
