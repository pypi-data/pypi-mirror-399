"""Comprehensive assertion tests covering different patterns."""


def test_equality():
    """Basic equality."""
    assert 1 == 1


def test_inequality():
    """Not equal check."""
    assert 1 != 2


def test_less_than():
    """Less than comparison."""
    assert 1 < 2


def test_greater_than():
    """Greater than comparison."""
    assert 2 > 1


def test_less_equal():
    """Less than or equal."""
    assert 1 <= 1
    assert 1 <= 2


def test_greater_equal():
    """Greater than or equal."""
    assert 2 >= 2
    assert 2 >= 1


def test_in_operator():
    """Membership test."""
    assert 1 in [1, 2, 3]
    assert "a" in "abc"
    assert "key" in {"key": "value"}


def test_not_in_operator():
    """Negative membership test."""
    assert 4 not in [1, 2, 3]
    assert "z" not in "abc"


def test_is_operator():
    """Identity test."""
    a = None
    assert a is None


def test_is_not_operator():
    """Negative identity test."""
    a = []
    assert a is not None


def test_boolean_expressions():
    """Boolean logic."""
    assert True and True
    assert True or False
    assert not False


def test_chained_comparisons():
    """Chained comparisons."""
    x = 5
    assert 1 < x < 10
    assert 0 <= x <= 10


def test_with_message():
    """Assert with custom message should pass."""
    x = 5
    assert x == 5, "x should be 5"


def test_string_methods():
    """String method assertions."""
    s = "Hello, World!"
    assert s.startswith("Hello")
    assert s.endswith("!")
    assert "World" in s
    assert s.lower() == "hello, world!"


def test_list_operations():
    """List operation assertions."""
    items = [1, 2, 3]
    assert len(items) == 3
    assert items[0] == 1
    assert items[-1] == 3
    assert sum(items) == 6


def test_dict_operations():
    """Dictionary operation assertions."""
    d = {"a": 1, "b": 2}
    assert len(d) == 2
    assert "a" in d
    assert d.get("c", 0) == 0


def test_set_operations():
    """Set operation assertions."""
    s1 = {1, 2, 3}
    s2 = {2, 3, 4}
    assert s1 & s2 == {2, 3}
    assert s1 | s2 == {1, 2, 3, 4}


def test_type_checks():
    """Type checking assertions."""
    assert isinstance(1, int)
    assert isinstance("a", str)
    assert isinstance([], list)
    assert issubclass(bool, int)


def test_callable_check():
    """Callable assertions."""
    def func():
        pass
    assert callable(func)
    assert not callable(42)


class TestAssertionsInClass:
    """Class-based assertion tests."""

    def test_instance_equality(self):
        """Instance-level test."""
        self.value = 42
        assert self.value == 42

    def test_multiple_assertions(self):
        """Multiple assertions in one test."""
        x = 10
        y = 20
        assert x < y
        assert x + y == 30
        assert x * 2 == y
