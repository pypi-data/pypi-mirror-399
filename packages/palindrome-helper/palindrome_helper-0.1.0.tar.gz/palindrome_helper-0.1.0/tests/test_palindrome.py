import pytest
from palindrome_helper.palindrome import is_palindrome


def test_palindrome_with_number():
    assert is_palindrome(121) is True
    assert is_palindrome(123) is False


def test_palindrome_with_string():
    assert is_palindrome("madam") is True
    assert is_palindrome("hello") is False


def test_palindrome_with_mixed_case():
    assert is_palindrome("Madam") is True


def test_palindrome_with_spaces():
    assert is_palindrome("Never odd or even") is True


def test_palindrome_edge_cases():
    assert is_palindrome("") is True
    assert is_palindrome(0) is True