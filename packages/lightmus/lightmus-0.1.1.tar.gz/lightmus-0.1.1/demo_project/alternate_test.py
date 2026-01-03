"""Test file using *_test.py naming pattern (alternate pattern)."""


def test_alternate_pattern_discovery():
    """Verify this file is discovered with *_test.py pattern."""
    assert True


def test_alternate_pattern_runs():
    """Another test in alternate pattern file."""
    assert 1 + 1 == 2


class TestAlternatePatternClass:
    """Class in alternate pattern file."""

    def test_method_in_alternate_pattern(self):
        """Method test in alternate pattern file."""
        assert "test" in "testing"
