"""Tests demonstrating error handling."""


def test_raises_value_error():
    raise ValueError("Intentional error")


class TestWithSetupFailure:
    def setup_method(self):
        raise RuntimeError("Setup failed intentionally")

    def test_never_runs(self):
        assert True
