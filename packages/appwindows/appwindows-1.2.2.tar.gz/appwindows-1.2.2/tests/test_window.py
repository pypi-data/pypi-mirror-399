import time

import numpy as np
import pytest

from appwindows import get_finder
from appwindows.geometry import Point, Size
from appwindows.exceptions import WindowDoesNotValidException

from window_creator import WindowCreator

creator = WindowCreator()

@pytest.fixture
def test_window():
    creator.create_window("Test Window for Operations")
    time.sleep(1)
    finder = get_finder()
    window = finder.get_window_by_title("Test Window for Operations")
    assert window is not None
    return window


def test_window_get_title(test_window):
    title = test_window.get_title()
    assert isinstance(title, str)
    assert "Test Window for Operations" in title


def test_window_get_points(test_window):
    quad_points = test_window.get_points()
    assert hasattr(quad_points, 'left_top')
    assert hasattr(quad_points, 'right_top')
    assert hasattr(quad_points, 'right_bottom')
    assert hasattr(quad_points, 'left_bottom')

    assert isinstance(quad_points.left_top, Point)
    assert isinstance(quad_points.right_top, Point)
    assert isinstance(quad_points.right_bottom, Point)
    assert isinstance(quad_points.left_bottom, Point)


def test_window_get_size(test_window):
    appwindows_size = test_window.get_size()
    assert isinstance(appwindows_size, Size)
    assert appwindows_size.width > 0
    assert appwindows_size.height > 0


def test_window_get_screenshot(test_window):
    screenshot = test_window.get_screenshot()
    assert screenshot is not None
    assert isinstance(screenshot, np.ndarray)
    assert len(screenshot.shape) >= 2


def test_window_move(test_window):
    current_points = test_window.get_points()
    current_x = current_points.left_top.x
    current_y = current_points.left_top.y

    new_point = Point(current_x + 50, current_y + 50)
    test_window.move(new_point)

    time.sleep(0.5)
    updated_points = test_window.get_points()
    assert updated_points.left_top.x == current_x + 50
    assert updated_points.left_top.y == current_y + 50


def test_window_resize(test_window):
    current_size = test_window.get_size()
    width_append = 100
    height_append = 50
    test_window.resize(Size(current_size.width + width_append, current_size.height + height_append))
    time.sleep(0.5)
    updated_size = test_window.get_size()
    assert updated_size.width == current_size.width + width_append
    assert updated_size.height == current_size.height + height_append


def test_window_close(test_window):
    test_window.close()
    time.sleep(1)

    with pytest.raises(WindowDoesNotValidException):
        test_window.to_background()


def test_close_all():
    creator.cleanup()