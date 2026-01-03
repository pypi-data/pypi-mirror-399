"""Tests for exception handling patterns."""


def test_try_except():
    try:
        result = 10 / 2
    except ZeroDivisionError:
        result = 0
    assert result == 5.0


def test_catch_specific_exception():
    caught = False
    try:
        int("not a number")
    except ValueError:
        caught = True
    assert caught


def test_multiple_except():
    def process(value):
        try:
            return int(value) / value
        except (ValueError, ZeroDivisionError):
            return -1

    assert process(0) == -1
    assert process("x") == -1


def test_except_as():
    message = ""
    try:
        raise ValueError("test error")
    except ValueError as e:
        message = str(e)
    assert message == "test error"


def test_finally():
    cleanup_done = False

    def operation():
        nonlocal cleanup_done
        try:
            return 42
        finally:
            cleanup_done = True

    result = operation()
    assert result == 42
    assert cleanup_done


def test_finally_with_exception():
    cleanup_done = False
    caught = False

    try:
        try:
            raise ValueError("error")
        finally:
            cleanup_done = True
    except ValueError:
        caught = True

    assert cleanup_done
    assert caught


def test_else_clause():
    executed_else = False
    try:
        result = 10 / 2
    except ZeroDivisionError:
        result = 0
    else:
        executed_else = True
    assert result == 5.0
    assert executed_else


def test_raise():
    caught = False
    try:
        raise RuntimeError("custom error")
    except RuntimeError:
        caught = True
    assert caught


def test_reraise():
    def inner():
        try:
            raise ValueError("inner")
        except ValueError:
            raise

    caught = False
    try:
        inner()
    except ValueError:
        caught = True
    assert caught


def test_chained_exception():
    try:
        try:
            raise ValueError("original")
        except ValueError as e:
            raise RuntimeError("wrapper") from e
    except RuntimeError as e:
        assert e.__cause__ is not None
        assert str(e.__cause__) == "original"


def test_custom_exception():
    class CustomError(Exception):
        def __init__(self, code, message):
            self.code = code
            self.message = message
            super().__init__(message)

    try:
        raise CustomError(404, "Not found")
    except CustomError as e:
        assert e.code == 404
        assert e.message == "Not found"


class TestExceptionHierarchy:
    def test_base_exception(self):
        assert issubclass(Exception, BaseException)

    def test_value_error(self):
        assert issubclass(ValueError, Exception)

    def test_type_error(self):
        assert issubclass(TypeError, Exception)

    def test_runtime_error(self):
        assert issubclass(RuntimeError, Exception)

    def test_key_error(self):
        assert issubclass(KeyError, LookupError)

    def test_index_error(self):
        assert issubclass(IndexError, LookupError)


class TestContextManager:
    def test_context_manager_enter_exit(self):
        class Resource:
            def __init__(self):
                self.opened = False
                self.closed = False

            def __enter__(self):
                self.opened = True
                return self

            def __exit__(self, exc_type, exc_val, exc_tb):
                self.closed = True
                return False

        r = Resource()
        with r:
            assert r.opened
        assert r.closed

    def test_context_manager_exception_handling(self):
        class SuppressError:
            def __enter__(self):
                return self

            def __exit__(self, exc_type, exc_val, exc_tb):
                return exc_type == ValueError

        with SuppressError():
            raise ValueError("suppressed")
