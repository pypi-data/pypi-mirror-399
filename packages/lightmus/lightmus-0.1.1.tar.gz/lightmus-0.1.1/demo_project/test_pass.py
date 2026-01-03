"""Tests that should all pass."""


def test_simple_pass():
    assert True


def test_arithmetic():
    assert 2 + 2 == 4


def test_string_operations():
    assert "hello".upper() == "HELLO"


class TestBasic:
    def test_method_pass(self):
        assert "hello".upper() == "HELLO"

    def test_list_operations(self):
        items = [1, 2, 3]
        items.append(4)
        assert len(items) == 4
