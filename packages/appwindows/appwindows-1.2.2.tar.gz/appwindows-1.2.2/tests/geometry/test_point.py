import pytest

from appwindows.geometry import Point


def test_point_addition():
    p1 = Point(1, 2)
    p2 = Point(3, 4)
    result = p1 + p2
    assert result.x == 4
    assert result.y == 6
    assert isinstance(result, Point)

def test_point_subtraction():
    p1 = Point(5, 6)
    p2 = Point(2, 3)
    result = p1 - p2
    assert result.x == 3
    assert result.y == 3
    assert isinstance(result, Point)

def test_point_division():
    p1 = Point(10, 15)
    p2 = Point(2, 3)
    result = p1 / p2
    assert result.x == 5
    assert result.y == 5
    assert isinstance(result, Point)

def test_point_division_by_zero():
    p1 = Point(10, 10)
    p2 = Point(0, 0)
    with pytest.raises(ValueError):
        p1 / p2

def test_point_multiplication():
    p1 = Point(2, 3)
    p2 = Point(4, 5)
    result = p1 * p2
    assert result.x == 8
    assert result.y == 15
    assert isinstance(result, Point)

def test_point_equality_same_points():
    p1 = Point(1, 2)
    p2 = Point(1, 2)
    assert p1 == p2

def test_point_equality_different_points():
    p1 = Point(1, 2)
    p2 = Point(3, 4)
    assert p1 != p2

def test_point_in_place_addition():
    p1 = Point(1, 2)
    p2 = Point(3, 4)
    p1 += p2
    assert p1.x == 4
    assert p1.y == 6

def test_point_in_place_subtraction():
    p1 = Point(5, 6)
    p2 = Point(2, 3)
    p1 -= p2
    assert p1.x == 3
    assert p1.y == 3

def test_point_in_place_multiplication():
    p1 = Point(2, 3)
    p2 = Point(4, 5)
    p1 *= p2
    assert p1.x == 8
    assert p1.y == 15

def test_point_in_place_division():
    p1 = Point(10, 15)
    p2 = Point(2, 3)
    p1 /= p2
    assert p1.x == 5
    assert p1.y == 5

def test_point_initialization():
    point = Point(10, 20)
    assert point.x == 10
    assert point.y == 20

def test_point_negative_coordinates():
    point = Point(-5, -15)
    assert point.x == -5
    assert point.y == -15

def test_point_zero_coordinates():
    point = Point(0, 0)
    assert point.x == 0
    assert point.y == 0

def test_point_equality():
    point1 = Point(10, 20)
    point2 = Point(10, 20)
    point3 = Point(30, 40)
    
    assert point1 == point2
    assert point1 != point3
