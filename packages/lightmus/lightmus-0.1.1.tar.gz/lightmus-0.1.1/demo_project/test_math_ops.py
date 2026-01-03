"""Tests for mathematical operations."""
import math


def test_addition():
    assert 2 + 3 == 5


def test_subtraction():
    assert 10 - 4 == 6


def test_multiplication():
    assert 3 * 4 == 12


def test_division():
    assert 15 / 3 == 5.0


def test_floor_division():
    assert 17 // 5 == 3


def test_modulo():
    assert 17 % 5 == 2


def test_power():
    assert 2 ** 10 == 1024


def test_abs():
    assert abs(-5) == 5


def test_round():
    assert round(3.7) == 4
    assert round(3.14159, 2) == 3.14


def test_min():
    assert min(3, 1, 4, 1, 5) == 1


def test_max():
    assert max(3, 1, 4, 1, 5) == 5


def test_sum():
    assert sum([1, 2, 3, 4]) == 10


def test_divmod():
    q, r = divmod(17, 5)
    assert q == 3 and r == 2


def test_float_precision():
    result = 0.1 + 0.2
    assert abs(result - 0.3) < 1e-10


def test_integer_division_negative():
    assert -7 // 3 == -3


def test_modulo_negative():
    assert -7 % 3 == 2


def test_math_sqrt():
    assert math.sqrt(16) == 4.0


def test_math_ceil():
    assert math.ceil(3.2) == 4


def test_math_floor():
    assert math.floor(3.8) == 3


def test_math_factorial():
    assert math.factorial(5) == 120


def test_math_gcd():
    assert math.gcd(48, 18) == 6


def test_math_pi():
    assert 3.14 < math.pi < 3.15


def test_math_e():
    assert 2.71 < math.e < 2.72


def test_math_log():
    assert abs(math.log(math.e) - 1.0) < 1e-10


def test_math_log10():
    assert math.log10(100) == 2.0


def test_math_sin():
    assert abs(math.sin(0)) < 1e-10


def test_math_cos():
    assert abs(math.cos(0) - 1.0) < 1e-10


class TestMathClass:
    def test_complex_expression(self):
        result = (2 + 3) * 4 - 10 / 2
        assert result == 15.0

    def test_power_chain(self):
        assert 2 ** 2 ** 3 == 256

    def test_operator_precedence(self):
        assert 2 + 3 * 4 == 14
        assert (2 + 3) * 4 == 20
