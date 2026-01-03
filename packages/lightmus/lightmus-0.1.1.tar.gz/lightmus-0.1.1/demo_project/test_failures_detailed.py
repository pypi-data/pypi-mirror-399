"""Tests demonstrating various failure modes for introspection."""


def test_fail_equality_literals():
    """Fail with literal values."""
    assert 1 == 2


def test_fail_equality_variables():
    """Fail with variable introspection."""
    expected = 100
    actual = 42
    assert actual == expected


def test_fail_inequality():
    """Fail not equal."""
    x = 5
    y = 5
    assert x != y


def test_fail_less_than():
    """Fail less than."""
    big = 100
    small = 10
    assert big < small


def test_fail_in_list():
    """Fail membership test."""
    needle = "missing"
    haystack = ["a", "b", "c"]
    assert needle in haystack


def test_fail_is_none():
    """Fail identity test."""
    value = "not none"
    assert value is None


def test_fail_boolean():
    """Fail boolean assertion."""
    condition = False
    assert condition


def test_fail_len():
    """Fail length check."""
    items = [1, 2, 3]
    assert len(items) == 5


def test_fail_nested_attribute():
    """Fail with nested attribute access."""
    class Inner:
        value = 10

    class Outer:
        inner = Inner()

    obj = Outer()
    assert obj.inner.value == 999


def test_fail_with_computation():
    """Fail with computed values."""
    a = 5
    b = 7
    result = a * b
    assert result == 100


class TestFailuresInClass:
    """Class-based failure tests."""

    def test_fail_method_basic(self):
        """Basic method failure."""
        assert False

    def test_fail_method_with_state(self):
        """Failure with instance state."""
        self.data = [1, 2, 3]
        assert len(self.data) == 10
