import pytest

from appwindows.geometry import Size
from appwindows.exceptions import InvalidSizeException


def test_size_initialization_valid():
    size = Size(100, 200)
    assert size.width == 100
    assert size.height == 200

def test_size_initialization_minimum():
    size = Size(1, 1)
    assert size.width == 1
    assert size.height == 1

def test_size_initialization_zero():
    with pytest.raises(InvalidSizeException):
        Size(0, 100)
        Size(100, 0)

def test_size_initialization_negative():
    with pytest.raises(InvalidSizeException):
        Size(-50, 100)
        Size(100, -50)
        Size(-50, -50)