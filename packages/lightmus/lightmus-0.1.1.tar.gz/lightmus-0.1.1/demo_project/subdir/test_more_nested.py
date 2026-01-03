"""Additional tests in nested directory."""


def test_nested_dir_math():
    assert 2 * 3 == 6


def test_nested_dir_string():
    assert "test".upper() == "TEST"


def test_nested_dir_list():
    items = [1, 2, 3]
    items.append(4)
    assert len(items) == 4


def test_nested_dir_dict():
    d = {"a": 1}
    d["b"] = 2
    assert d == {"a": 1, "b": 2}


class TestNestedDirClass:
    def test_method_in_nested(self):
        assert True

    def test_another_method(self):
        assert 1 + 1 == 2
