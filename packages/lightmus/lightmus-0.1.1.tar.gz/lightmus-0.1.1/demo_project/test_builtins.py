"""Tests for Python builtin functions."""


def test_len():
    assert len([1, 2, 3]) == 3
    assert len("hello") == 5
    assert len({1, 2, 3}) == 3


def test_range():
    assert list(range(5)) == [0, 1, 2, 3, 4]
    assert list(range(2, 5)) == [2, 3, 4]
    assert list(range(0, 10, 2)) == [0, 2, 4, 6, 8]


def test_enumerate():
    result = list(enumerate(["a", "b", "c"]))
    assert result == [(0, "a"), (1, "b"), (2, "c")]


def test_zip():
    result = list(zip([1, 2], ["a", "b"]))
    assert result == [(1, "a"), (2, "b")]


def test_map():
    result = list(map(lambda x: x * 2, [1, 2, 3]))
    assert result == [2, 4, 6]


def test_filter():
    result = list(filter(lambda x: x > 2, [1, 2, 3, 4]))
    assert result == [3, 4]


def test_sorted():
    assert sorted([3, 1, 2]) == [1, 2, 3]
    assert sorted([3, 1, 2], reverse=True) == [3, 2, 1]


def test_reversed():
    assert list(reversed([1, 2, 3])) == [3, 2, 1]


def test_any():
    assert any([False, True, False])
    assert not any([False, False, False])


def test_all():
    assert all([True, True, True])
    assert not all([True, False, True])


def test_isinstance():
    assert isinstance(1, int)
    assert isinstance("a", str)
    assert isinstance([1], list)


def test_issubclass():
    assert issubclass(bool, int)
    assert issubclass(list, object)


def test_type():
    assert type(1) == int
    assert type("a") == str


def test_id():
    a = [1, 2, 3]
    b = a
    assert id(a) == id(b)


def test_hash():
    assert hash("hello") == hash("hello")
    assert hash(42) == hash(42)


def test_callable():
    def func():
        pass
    assert callable(func)
    assert not callable(42)


def test_getattr():
    class Obj:
        value = 42
    assert getattr(Obj, "value") == 42
    assert getattr(Obj, "missing", 0) == 0


def test_hasattr():
    class Obj:
        value = 42
    assert hasattr(Obj, "value")
    assert not hasattr(Obj, "missing")


def test_setattr():
    class Obj:
        pass
    obj = Obj()
    setattr(obj, "value", 42)
    assert obj.value == 42


def test_delattr():
    class Obj:
        value = 42
    obj = Obj()
    obj.value = 100
    delattr(obj, "value")
    assert obj.value == 42


def test_vars():
    class Obj:
        def __init__(self):
            self.a = 1
            self.b = 2
    obj = Obj()
    v = vars(obj)
    assert v["a"] == 1
    assert v["b"] == 2


def test_dir():
    result = dir([])
    assert "append" in result
    assert "pop" in result


class TestBuiltinClass:
    def test_repr(self):
        assert repr(42) == "42"
        assert repr("hello") == "'hello'"

    def test_str(self):
        assert str(42) == "42"
        assert str([1, 2]) == "[1, 2]"

    def test_bool(self):
        assert bool(1) is True
        assert bool(0) is False
        assert bool([]) is False
        assert bool([1]) is True

    def test_int_conversion(self):
        assert int("42") == 42
        assert int(3.9) == 3

    def test_float_conversion(self):
        assert float("3.14") == 3.14
        assert float(42) == 42.0
