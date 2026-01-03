from appwindows import get_finder


def test_get_finder_function():
    finder = get_finder()
    assert finder is not None
    
def test_get_finder_returns_finder_instance():
    from appwindows import Finder
    finder = get_finder()
    assert isinstance(finder, Finder)
    
def test_multiple_get_finder_calls():
    finder1 = get_finder()
    finder2 = get_finder()
    assert finder1 is not None
    assert finder2 is not None