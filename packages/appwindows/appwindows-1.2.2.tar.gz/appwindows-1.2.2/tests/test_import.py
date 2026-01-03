def test_import_appwindows():
    import appwindows
    assert appwindows is not None
    
def test_import_get_finder():
    from appwindows import get_finder
    assert callable(get_finder)
    
def test_import_geometry_modules():
    from appwindows.geometry import Point, Size, QuadPoints
    assert Point is not None
    assert Size is not None
    assert QuadPoints is not None
    
def test_import_finder_and_window():
    from appwindows import Finder, Window
    assert Finder is not None
    assert Window is not None