"""Tests for iterators and generators."""


def test_iter():
    items = [1, 2, 3]
    it = iter(items)
    assert next(it) == 1
    assert next(it) == 2
    assert next(it) == 3


def test_next_default():
    it = iter([1])
    assert next(it) == 1
    assert next(it, "done") == "done"


def test_for_loop_iteration():
    result = []
    for x in [1, 2, 3]:
        result.append(x * 2)
    assert result == [2, 4, 6]


def test_list_from_iterator():
    result = list(range(5))
    assert result == [0, 1, 2, 3, 4]


def test_generator_function():
    def gen():
        yield 1
        yield 2
        yield 3

    result = list(gen())
    assert result == [1, 2, 3]


def test_generator_expression():
    gen = (x * 2 for x in range(3))
    result = list(gen)
    assert result == [0, 2, 4]


def test_generator_with_condition():
    def evens(n):
        for i in range(n):
            if i % 2 == 0:
                yield i

    result = list(evens(10))
    assert result == [0, 2, 4, 6, 8]


def test_generator_send():
    def accumulator():
        total = 0
        while True:
            value = yield total
            if value is None:
                break
            total += value

    gen = accumulator()
    next(gen)
    assert gen.send(1) == 1
    assert gen.send(2) == 3
    assert gen.send(3) == 6


def test_yield_from():
    def inner():
        yield 1
        yield 2

    def outer():
        yield from inner()
        yield 3

    result = list(outer())
    assert result == [1, 2, 3]


def test_infinite_generator():
    def counter():
        n = 0
        while True:
            yield n
            n += 1

    gen = counter()
    assert next(gen) == 0
    assert next(gen) == 1
    assert next(gen) == 2


def test_custom_iterator():
    class Countdown:
        def __init__(self, start):
            self.start = start

        def __iter__(self):
            return self

        def __next__(self):
            if self.start <= 0:
                raise StopIteration
            self.start -= 1
            return self.start + 1

    result = list(Countdown(3))
    assert result == [3, 2, 1]


def test_itertools_chain():
    from itertools import chain
    result = list(chain([1, 2], [3, 4]))
    assert result == [1, 2, 3, 4]


def test_itertools_repeat():
    from itertools import repeat
    result = list(repeat("x", 3))
    assert result == ["x", "x", "x"]


def test_itertools_takewhile():
    from itertools import takewhile
    result = list(takewhile(lambda x: x < 5, [1, 3, 5, 7, 2]))
    assert result == [1, 3]


def test_itertools_dropwhile():
    from itertools import dropwhile
    result = list(dropwhile(lambda x: x < 5, [1, 3, 5, 7, 2]))
    assert result == [5, 7, 2]


class TestIteratorProtocol:
    def test_iter_returns_self(self):
        class MyIter:
            def __iter__(self):
                return self

            def __next__(self):
                raise StopIteration

        it = MyIter()
        assert iter(it) is it

    def test_iterable_vs_iterator(self):
        items = [1, 2, 3]
        it = iter(items)
        assert hasattr(items, "__iter__")
        assert hasattr(it, "__next__")
