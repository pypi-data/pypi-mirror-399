"""Tests for edge cases and special scenarios."""


# Non-test functions should be ignored
def helper_function():
    """This is not a test - should be ignored."""
    return 42


def utility():
    """Another non-test function."""
    pass


# Private functions should be ignored
def _test_private():
    """Starts with underscore - should be ignored."""
    assert False  # Would fail if run


def __test_dunder_like():
    """Starts with double underscore - should be ignored."""
    assert False  # Would fail if run


# Test with pass only
def test_empty_pass():
    """Test that just passes."""
    pass


# Test with docstring only
def test_docstring_only():
    """This test has only a docstring."""


# Test using walrus operator
def test_walrus_operator():
    """Test using := operator."""
    if (n := 10) > 5:
        assert n == 10


# Test with f-string in assertion
def test_fstring_assertion():
    """Test with f-string."""
    name = "world"
    greeting = f"Hello, {name}!"
    assert greeting == "Hello, world!"


# Test with comprehension
def test_comprehension():
    """Test with list comprehension."""
    squares = [x**2 for x in range(5)]
    assert squares == [0, 1, 4, 9, 16]


# Test with generator expression
def test_generator():
    """Test with generator expression."""
    total = sum(x for x in range(10))
    assert total == 45


# Test with lambda
def test_lambda():
    """Test with lambda function."""
    double = lambda x: x * 2
    assert double(21) == 42


# Test with context manager
def test_context_manager():
    """Test using context manager."""
    from io import StringIO
    with StringIO("test") as f:
        assert f.read() == "test"


# Test with exception handling inside test
def test_expected_exception():
    """Test that catches expected exception."""
    try:
        raise ValueError("expected")
    except ValueError as e:
        assert str(e) == "expected"


# Non-Test class should be ignored
class HelperClass:
    """Not a test class - doesn't start with Test."""

    def test_method(self):
        """Would fail if discovered."""
        assert False


# Nested class should be ignored
class TestOuterClass:
    """Test class with nested class."""

    def test_outer_method(self):
        """Test in outer class - should run."""
        assert True

    class NestedTestClass:
        """Nested class - should be ignored."""

        def test_nested_method(self):
            """Would fail if discovered."""
            assert False


# Class without Test prefix
class SomeTests:
    """Doesn't start with 'Test' - should be ignored."""

    def test_method(self):
        """Would fail if discovered."""
        assert False
