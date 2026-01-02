import pytest

from dbl_core.events.canonical import canonicalize_value


def test_mapping_key_must_be_str():
    with pytest.raises(TypeError, match="mapping key must be str"):
        canonicalize_value({1: "x"})  # type: ignore[dict-item]


def test_set_must_be_primitive_only():
    with pytest.raises(TypeError, match="set values must be JSON primitives"):
        canonicalize_value({"s": {("x",)}})  # tuple in set


def test_set_sort_is_deterministic():
    a = canonicalize_value({"s": {"b", "a"}})
    b = canonicalize_value({"s": {"a", "b"}})
    assert a == b


class _HasToDict:
    def to_dict(self):
        return {"x": 1}


def test_object_with_to_dict_is_rejected():
    with pytest.raises(TypeError, match="non-serializable type in canonicalization"):
        canonicalize_value(_HasToDict())


def test_float_is_rejected():
    with pytest.raises(TypeError, match="float is not allowed"):
        canonicalize_value({"x": 0.1})
