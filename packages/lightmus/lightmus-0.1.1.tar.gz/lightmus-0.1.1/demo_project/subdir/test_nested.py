"""Tests in a nested directory to verify recursive discovery."""


def test_nested_pass():
    assert True


def test_nested_list():
    items = [1, 2, 3]
    assert 2 in items


class TestNested:
    def test_method_in_nested(self):
        assert "abc".startswith("a")
