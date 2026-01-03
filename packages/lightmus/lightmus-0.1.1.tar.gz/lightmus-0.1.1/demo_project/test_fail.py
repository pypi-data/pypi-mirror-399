"""Tests demonstrating failure reporting."""


def test_simple_assertion():
    assert 1 == 2


def test_variable_assertion():
    x = 10
    y = 12
    assert x == y


class TestFailures:
    def test_attribute_access(self):
        class Obj:
            value = 42

        obj = Obj()
        expected = 99
        assert obj.value == expected

    def test_list_index(self):
        arr = [1, 2, 3]
        assert arr[0] == 100
