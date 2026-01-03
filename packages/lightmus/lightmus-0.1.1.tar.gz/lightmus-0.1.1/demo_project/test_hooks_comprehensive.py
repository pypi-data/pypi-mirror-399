"""Tests for all setup/teardown hook combinations."""

_module_log: list[str] = []


def setup_module():
    """Module-level setup."""
    _module_log.append("setup_module")


def teardown_module():
    """Module-level teardown."""
    _module_log.append("teardown_module")


def test_module_setup_ran():
    """Verify module setup ran."""
    assert "setup_module" in _module_log


def test_module_setup_only_once():
    """Verify module setup ran exactly once."""
    assert _module_log.count("setup_module") == 1


class TestWithAllHooks:
    """Class with all four hook types."""

    _class_log: list[str] = []

    @classmethod
    def setup_class(cls):
        """Class-level setup."""
        cls._class_log.append("setup_class")

    @classmethod
    def teardown_class(cls):
        """Class-level teardown."""
        cls._class_log.append("teardown_class")

    def setup_method(self):
        """Method-level setup - runs before each test."""
        self._class_log.append("setup_method")

    def teardown_method(self):
        """Method-level teardown - runs after each test."""
        self._class_log.append("teardown_method")

    def test_class_setup_ran(self):
        """Verify class setup ran."""
        assert "setup_class" in self._class_log

    def test_method_setup_ran(self):
        """Verify method setup ran."""
        assert "setup_method" in self._class_log

    def test_multiple_method_setups(self):
        """By now, setup_method should have run multiple times."""
        count = self._class_log.count("setup_method")
        assert count >= 1  # At least once for this test


class TestWithOnlySetupMethod:
    """Class with only setup_method."""

    def setup_method(self):
        """Per-test setup."""
        self.prepared = True

    def test_setup_worked(self):
        """Verify setup ran."""
        assert self.prepared is True


class TestWithOnlyTeardownMethod:
    """Class with only teardown_method."""

    def teardown_method(self):
        """Per-test cleanup - still runs."""
        pass

    def test_runs_fine(self):
        """Test runs without setup."""
        assert True


class TestWithOnlyClassHooks:
    """Class with only class-level hooks."""

    _initialized = False

    @classmethod
    def setup_class(cls):
        """Initialize once for all tests."""
        cls._initialized = True

    @classmethod
    def teardown_class(cls):
        """Clean up once after all tests."""
        cls._initialized = False

    def test_initialized(self):
        """Verify class was initialized."""
        assert self._initialized is True


class TestWithNoHooks:
    """Class without any hooks - should work fine."""

    def test_no_hooks_needed(self):
        """Test without any hooks."""
        assert 1 + 1 == 2

    def test_another_without_hooks(self):
        """Another test without hooks."""
        assert "hello" == "hello"
