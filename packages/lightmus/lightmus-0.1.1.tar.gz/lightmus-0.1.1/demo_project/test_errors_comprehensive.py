"""Tests for error scenarios and exception handling."""


def test_raises_value_error():
    """Raises ValueError - should be ERROR (or FAILED in pytest-compat)."""
    raise ValueError("Intentional ValueError")


def test_raises_type_error():
    """Raises TypeError."""
    raise TypeError("Intentional TypeError")


def test_raises_runtime_error():
    """Raises RuntimeError."""
    raise RuntimeError("Intentional RuntimeError")


def test_raises_key_error():
    """Raises KeyError."""
    d = {}
    _ = d["nonexistent"]


def test_raises_index_error():
    """Raises IndexError."""
    items = [1, 2, 3]
    _ = items[100]


def test_raises_attribute_error():
    """Raises AttributeError."""
    obj = object()
    _ = obj.nonexistent_attribute


def test_raises_zero_division():
    """Raises ZeroDivisionError."""
    _ = 1 / 0


def test_raises_with_traceback():
    """Exception with deeper traceback."""
    def inner():
        def innermost():
            raise Exception("Deep exception")
        innermost()
    inner()


class TestSetupFailures:
    """Class where setup fails."""

    def setup_method(self):
        """Setup that fails."""
        raise RuntimeError("Setup failed!")

    def test_never_runs_a(self):
        """This test should not run."""
        assert True

    def test_never_runs_b(self):
        """This test should also not run."""
        assert True


class TestClassSetupFailure:
    """Class where class setup fails."""

    @classmethod
    def setup_class(cls):
        """Class setup that fails."""
        raise RuntimeError("Class setup failed!")

    def test_never_runs(self):
        """This test should not run."""
        assert True


class TestTeardownFailure:
    """Class where teardown fails (test still passes, but teardown errors)."""

    def teardown_method(self):
        """Teardown that fails."""
        raise RuntimeError("Teardown failed!")

    def test_this_passes(self):
        """Test passes, but teardown will fail."""
        assert True


class TestExceptionInAssertion:
    """Exceptions raised during assertion evaluation."""

    def test_exception_in_assert_expression(self):
        """Exception during assert evaluation."""
        def bad_comparison():
            raise ValueError("Bad comparison")

        assert bad_comparison()
