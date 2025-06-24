"""Test geometry attribute access in CRUD operations."""

from nbsapi.schemas.geometry import LineStringGeometry, PolygonGeometry, PointGeometry


def test_geometry_type_attribute_access():
    """Test that geometry objects have proper type attribute access."""

    # Test LineString geometry
    linestring = LineStringGeometry(
        coordinates=[[4.9041, 52.3676], [4.9042, 52.3677], [4.9043, 52.3678]]
    )
    assert linestring.type == "LineString"
    assert hasattr(linestring, "type")

    # Test Polygon geometry
    polygon = PolygonGeometry(
        coordinates=[
            [[4.9041, 52.3676], [4.9042, 52.3677], [4.9043, 52.3678], [4.9041, 52.3676]]
        ]
    )
    assert polygon.type == "Polygon"
    assert hasattr(polygon, "type")

    # Test Point geometry
    point = PointGeometry(coordinates=[4.9041, 52.3676])
    assert point.type == "Point"
    assert hasattr(point, "type")


def test_geometry_objects_do_not_have_get_method():
    """Test that geometry objects don't have dict-like get method."""

    linestring = LineStringGeometry(
        coordinates=[[4.9041, 52.3676], [4.9042, 52.3677], [4.9043, 52.3678]]
    )

    # Should not have get method like a dict
    assert not hasattr(linestring, "get")

    # Should access type directly as attribute
    assert linestring.type == "LineString"


def test_geometry_type_comparison():
    """Test that geometry type comparison works correctly."""

    linestring = LineStringGeometry(
        coordinates=[[4.9041, 52.3676], [4.9042, 52.3677], [4.9043, 52.3678]]
    )

    polygon = PolygonGeometry(
        coordinates=[
            [[4.9041, 52.3676], [4.9042, 52.3677], [4.9043, 52.3678], [4.9041, 52.3676]]
        ]
    )

    # Test type comparison logic that would be used in CRUD operations
    is_linestring = linestring.type == "LineString"
    is_polygon = polygon.type == "Polygon"

    assert is_linestring is True
    assert is_polygon is True
    assert polygon.type != "LineString"
    assert linestring.type != "Polygon"
