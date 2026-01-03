"""Tests for string operations."""


def test_string_upper():
    assert "hello".upper() == "HELLO"


def test_string_lower():
    assert "HELLO".lower() == "hello"


def test_string_capitalize():
    assert "hello world".capitalize() == "Hello world"


def test_string_title():
    assert "hello world".title() == "Hello World"


def test_string_strip():
    assert "  hello  ".strip() == "hello"


def test_string_lstrip():
    assert "  hello".lstrip() == "hello"


def test_string_rstrip():
    assert "hello  ".rstrip() == "hello"


def test_string_split():
    parts = "a,b,c".split(",")
    assert parts == ["a", "b", "c"]


def test_string_join():
    result = "-".join(["a", "b", "c"])
    assert result == "a-b-c"


def test_string_replace():
    assert "hello".replace("l", "x") == "hexxo"


def test_string_find():
    assert "hello".find("l") == 2


def test_string_rfind():
    assert "hello".rfind("l") == 3


def test_string_count():
    assert "banana".count("a") == 3


def test_string_startswith():
    assert "hello".startswith("he")


def test_string_endswith():
    assert "hello".endswith("lo")


def test_string_isdigit():
    assert "123".isdigit()
    assert not "12a".isdigit()


def test_string_isalpha():
    assert "abc".isalpha()
    assert not "ab1".isalpha()


def test_string_isalnum():
    assert "abc123".isalnum()
    assert not "abc 123".isalnum()


def test_string_format():
    result = "Hello, {}!".format("World")
    assert result == "Hello, World!"


def test_fstring():
    name = "World"
    assert f"Hello, {name}!" == "Hello, World!"


def test_string_zfill():
    assert "42".zfill(5) == "00042"


def test_string_center():
    assert "hi".center(6) == "  hi  "


def test_string_ljust():
    assert "hi".ljust(5) == "hi   "


def test_string_rjust():
    assert "hi".rjust(5) == "   hi"


class TestStringMethods:
    def test_multiline_string(self):
        text = """line1
line2
line3"""
        lines = text.split("\n")
        assert len(lines) == 3

    def test_string_multiplication(self):
        assert "ab" * 3 == "ababab"

    def test_string_slicing(self):
        s = "hello"
        assert s[1:4] == "ell"
        assert s[:2] == "he"
        assert s[2:] == "llo"
        assert s[::-1] == "olleh"

    def test_string_in_operator(self):
        assert "ell" in "hello"
        assert "xyz" not in "hello"
