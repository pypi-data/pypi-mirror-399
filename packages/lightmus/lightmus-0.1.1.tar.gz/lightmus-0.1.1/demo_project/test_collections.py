"""Tests for collection types and operations."""


def test_list_append():
    items = []
    items.append(1)
    assert items == [1]


def test_list_extend():
    items = [1, 2]
    items.extend([3, 4])
    assert items == [1, 2, 3, 4]


def test_list_pop():
    items = [1, 2, 3]
    last = items.pop()
    assert last == 3
    assert len(items) == 2


def test_list_insert():
    items = [1, 3]
    items.insert(1, 2)
    assert items == [1, 2, 3]


def test_list_remove():
    items = [1, 2, 3, 2]
    items.remove(2)
    assert items == [1, 3, 2]


def test_list_reverse():
    items = [1, 2, 3]
    items.reverse()
    assert items == [3, 2, 1]


def test_list_sort():
    items = [3, 1, 2]
    items.sort()
    assert items == [1, 2, 3]


def test_list_copy():
    original = [1, 2, 3]
    copy = original.copy()
    copy.append(4)
    assert original == [1, 2, 3]
    assert copy == [1, 2, 3, 4]


def test_dict_get():
    d = {"a": 1, "b": 2}
    assert d.get("a") == 1
    assert d.get("c", 0) == 0


def test_dict_keys():
    d = {"a": 1, "b": 2}
    keys = list(d.keys())
    assert "a" in keys
    assert "b" in keys


def test_dict_values():
    d = {"a": 1, "b": 2}
    values = list(d.values())
    assert 1 in values
    assert 2 in values


def test_dict_items():
    d = {"a": 1}
    items = list(d.items())
    assert ("a", 1) in items


def test_dict_update():
    d = {"a": 1}
    d.update({"b": 2})
    assert d == {"a": 1, "b": 2}


def test_dict_pop():
    d = {"a": 1, "b": 2}
    value = d.pop("a")
    assert value == 1
    assert "a" not in d


def test_set_add():
    s = {1, 2}
    s.add(3)
    assert 3 in s


def test_set_remove():
    s = {1, 2, 3}
    s.remove(2)
    assert 2 not in s


def test_set_union():
    s1 = {1, 2}
    s2 = {2, 3}
    assert s1.union(s2) == {1, 2, 3}


def test_set_intersection():
    s1 = {1, 2, 3}
    s2 = {2, 3, 4}
    assert s1.intersection(s2) == {2, 3}


def test_set_difference():
    s1 = {1, 2, 3}
    s2 = {2, 3}
    assert s1.difference(s2) == {1}


def test_tuple_unpacking():
    t = (1, 2, 3)
    a, b, c = t
    assert a == 1 and b == 2 and c == 3


def test_tuple_index():
    t = (10, 20, 30)
    assert t[1] == 20


def test_tuple_count():
    t = (1, 2, 2, 3, 2)
    assert t.count(2) == 3


class TestCollectionMethods:
    def test_list_comprehension(self):
        squares = [x**2 for x in range(5)]
        assert squares == [0, 1, 4, 9, 16]

    def test_dict_comprehension(self):
        d = {x: x**2 for x in range(3)}
        assert d == {0: 0, 1: 1, 2: 4}

    def test_set_comprehension(self):
        s = {x % 3 for x in range(10)}
        assert s == {0, 1, 2}

    def test_generator_to_list(self):
        gen = (x * 2 for x in range(3))
        result = list(gen)
        assert result == [0, 2, 4]
