"""Tests in deeply nested subdirectory."""


def test_deeply_nested():
    """Test in deep directory structure."""
    assert True


def test_path_discovery():
    """Verify deep paths are discovered."""
    import os
    assert os.path.exists(__file__)


class TestDeepNested:
    """Class in deep directory."""

    def test_deep_method(self):
        """Method in deeply nested class."""
        assert "deep" in "deeply"
