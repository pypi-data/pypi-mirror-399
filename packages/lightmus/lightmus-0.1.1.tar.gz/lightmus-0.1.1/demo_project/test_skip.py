"""Tests demonstrating skip behavior."""


def test_with_required_args(x, y):
    """Should be skipped: unsupported signature."""
    assert x == y


def test_with_kwargs_only(*, optional=1):
    """Should run: no required positional args."""
    assert optional == 1


def test_with_defaults(a=1, b=2):
    """Should run: has defaults."""
    assert a + b == 3
