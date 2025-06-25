"""Test enhanced schemas with new v2 fields."""

from nbsapi.schemas.naturebasedsolution import NatureBasedSolutionCreate
from nbsapi.schemas.geometry import PolygonGeometry


def test_nbs_create_with_new_fields():
    """Test creating NBS with the new Deltares-compatible fields."""
    solution = NatureBasedSolutionCreate(
        name="Test Solution",
        definition="Test definition",
        cobenefits="Test benefits",
        specificdetails="Test details",
        location="Test location",
        geometry=PolygonGeometry(
            coordinates=[[[0, 0], [1, 0], [1, 1], [0, 1], [0, 0]]]
        ),
        measure_id="39",
        area=1000.0,
        length=50.0,
        impacts=[],
        adaptations=[],
    )

    assert solution.name == "Test Solution"
    assert solution.measure_id == "39"
    assert solution.area == 1000.0
    assert solution.length == 50.0
    assert solution.geometry.type == "Polygon"


def test_nbs_create_optional_fields():
    """Test creating NBS with minimal required fields."""
    solution = NatureBasedSolutionCreate(
        name="Minimal Solution",
        definition="Minimal definition",
        cobenefits="Minimal benefits",
        specificdetails="Minimal details",
        location="Minimal location",
        impacts=[],
        adaptations=[],
    )

    assert solution.name == "Minimal Solution"
    assert solution.measure_id is None
    assert solution.area is None
    assert solution.length is None
    assert solution.geometry is None
