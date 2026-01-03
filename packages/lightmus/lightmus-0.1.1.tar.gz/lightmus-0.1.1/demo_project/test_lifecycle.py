"""Tests demonstrating setup/teardown hooks."""

_log: list[str] = []


def setup_module():
    _log.append("setup_module")


def teardown_module():
    _log.append("teardown_module")


def test_module_hook_ran():
    assert "setup_module" in _log


class TestWithHooks:
    @classmethod
    def setup_class(cls):
        _log.append("setup_class")

    @classmethod
    def teardown_class(cls):
        _log.append("teardown_class")

    def setup_method(self):
        _log.append("setup_method")

    def teardown_method(self):
        _log.append("teardown_method")

    def test_class_hook_ran(self):
        assert "setup_class" in _log

    def test_method_hook_ran(self):
        assert "setup_method" in _log
