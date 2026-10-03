from shapely.geometry import Polygon, MultiPolygon
from flood_exposure.transform.buildings import to_multipolygon

def test_polygon_becomes_multipolygon():
    out = to_multipolygon(Polygon([(0, 0), (1, 0), (1, 1), (0, 0)]))
    assert isinstance(out, MultiPolygon)
    assert len(out.geoms) == 1

def test_multipolygon_stays():
    mp = MultiPolygon([Polygon([(0, 0), (1, 0), (1, 1), (0, 0)])])
    assert to_multipolygon(mp) is mp

def test_empty_is_none():
    assert to_multipolygon(Polygon()) is None
