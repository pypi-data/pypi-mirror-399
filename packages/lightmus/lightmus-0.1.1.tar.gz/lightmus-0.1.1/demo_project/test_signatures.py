"""Tests for different signature patterns."""


# Should run - no required args
def test_no_args():
    assert True


# Should run - only default args
def test_with_defaults(a=1, b=2, c=3):
    assert a + b + c == 6


# Should run - keyword-only with defaults
def test_keyword_only_with_defaults(*, option=True):
    assert option is True


# Should run - *args only
def test_var_positional(*args):
    assert len(args) == 0


# Should run - **kwargs only
def test_var_keyword(**kwargs):
    assert len(kwargs) == 0


# Should run - mixed defaults
def test_mixed_defaults(required=10, *args, keyword=True, **kwargs):
    assert required == 10
    assert keyword is True


# Should be SKIPPED - required positional arg
def test_required_positional(x):
    assert x == 1


# Should be SKIPPED - required positional args
def test_multiple_required(x, y, z):
    assert x + y + z == 6


# Should be SKIPPED - required before default
def test_required_before_default(x, y=10):
    assert x + y == 11


# Should be SKIPPED - positional only required (Python 3.8+)
def test_positional_only_required(x, /, y=10):
    assert x + y == 11


# Should run - positional only with default
def test_positional_only_with_default(x=5, /):
    assert x == 5


# Should be SKIPPED - keyword only required
def test_keyword_only_required(*, required):
    assert required is True


class TestSignaturesInClass:
    """Class-based signature tests."""

    # Should run - self is handled
    def test_method_no_extra_args(self):
        assert True

    # Should run - self + defaults
    def test_method_with_defaults(self, value=42):
        assert value == 42

    # Should be SKIPPED - self + required
    def test_method_with_required(self, required):
        assert required is not None

    # Should run - **kwargs after self
    def test_method_with_kwargs(self, **kwargs):
        assert len(kwargs) == 0
