import pytest

from app.tools.calculator import calculate


def test_addition():
    assert calculate("10 + 5") == 15


def test_multiplication():
    assert calculate("6 * 7") == 42


def test_division():
    assert calculate("100 / 4") == 25


def test_power():
    assert calculate("2 ** 3") == 8


def test_negative_number():
    assert calculate("-5 + 10") == 5


def test_division_by_zero():
    with pytest.raises(ValueError, match="Cannot divide by zero"):
        calculate("10 / 0")


def test_invalid_expression():
    with pytest.raises(ValueError):
        calculate("hello")


def test_unsafe_expression():
    with pytest.raises(ValueError):
        calculate('__import__("os")')


def test_empty_expression():
    with pytest.raises(ValueError, match="Expression cannot be empty"):
        calculate("")