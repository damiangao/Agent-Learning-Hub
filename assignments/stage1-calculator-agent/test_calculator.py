"""
Tests for calculator tool.
"""
import pytest
from calculator import calculator


def test_calculator_simple_addition():
    """Calculator should handle simple addition."""
    result = calculator("2 + 3")
    assert result == "5"


def test_calculator_complex_expression():
    """Calculator should handle complex expressions."""
    result = calculator("23 * 17 + 5")
    assert result == "396"


def test_calculator_division():
    """Calculator should handle division."""
    result = calculator("10 / 2")
    assert result == "5.0"


def test_calculator_rejects_dangerous_expression():
    """Calculator should reject dangerous expressions."""
    result = calculator("__import__('os').system('rm -rf /')")
    assert "Error" in result


def test_calculator_handles_division_by_zero():
    """Calculator should handle division by zero gracefully."""
    result = calculator("1 / 0")
    assert "Error" in result
    assert "zero" in result.lower()


def test_calculator_rejects_invalid_syntax():
    """Calculator should reject invalid syntax."""
    result = calculator("2 +")
    assert "Error" in result
