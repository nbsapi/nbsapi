"""Test creating NBS without adaptations attribute."""

import pytest
from nbsapi.schemas.naturebasedsolution import NatureBasedSolutionCreate


def test_nbs_create_without_adaptations():
    """Test that NatureBasedSolutionCreate can be created without adaptations."""
    nbs_data = {
        "name": "Test Green Roof",
        "definition": "A test green roof installation",
        "cobenefits": "Urban cooling, biodiversity",
        "specificdetails": "Extensive green roof with sedum",
        "location": "Amsterdam",
        "geometry": {"type": "Point", "coordinates": [4.9041, 52.3676]},
    }

    nbs = NatureBasedSolutionCreate(**nbs_data)

    # Verify the object was created successfully
    assert nbs.name == "Test Green Roof"
    assert nbs.definition == "A test green roof installation"
    assert nbs.location == "Amsterdam"
    assert nbs.geometry.type == "Point"

    # Verify adaptations attribute doesn't exist
    assert not hasattr(nbs, "adaptations")


def test_nbs_create_with_impacts():
    """Test that NatureBasedSolutionCreate can include impacts."""
    nbs_data = {
        "name": "Test Rain Garden",
        "definition": "A test rain garden installation",
        "cobenefits": "Water management, biodiversity",
        "specificdetails": "Bioretention cell design",
        "location": "Utrecht",
        "impacts": [
            {
                "magnitude": 10.5,
                "unit": {"unit": "m2", "description": "shade"},
                "intensity": {"intensity": "low"},
            }
        ],
    }

    nbs = NatureBasedSolutionCreate(**nbs_data)

    # Verify the object was created successfully
    assert nbs.name == "Test Rain Garden"
    assert len(nbs.impacts) == 1
    assert nbs.impacts[0].magnitude == 10.5
    assert nbs.impacts[0].unit.unit == "m2"
    assert nbs.impacts[0].intensity.intensity == "low"


def test_nbs_create_minimal():
    """Test NatureBasedSolutionCreate with minimal required fields."""
    nbs_data = {
        "name": "Minimal NBS",
        "definition": "Minimal definition",
        "cobenefits": "Minimal benefits",
        "specificdetails": "Minimal details",
        "location": "Somewhere",
    }

    nbs = NatureBasedSolutionCreate(**nbs_data)

    # Verify required fields
    assert nbs.name == "Minimal NBS"
    assert nbs.definition == "Minimal definition"
    assert nbs.cobenefits == "Minimal benefits"
    assert nbs.specificdetails == "Minimal details"
    assert nbs.location == "Somewhere"

    # Verify optional fields
    assert nbs.geometry is None

    # Check that impacts exists but is empty or None
    if hasattr(nbs, "impacts"):
        assert nbs.impacts is None or len(nbs.impacts) == 0


def test_hasattr_adaptations_check():
    """Test that hasattr check for adaptations works correctly."""
    nbs = NatureBasedSolutionCreate(
        name="Test NBS",
        definition="Test definition",
        cobenefits="Test benefits",
        specificdetails="Test details",
        location="Test location",
    )

    # This should return False since adaptations don't exist in v2 schema
    assert not hasattr(nbs, "adaptations")

    # This should not raise an exception
    if hasattr(nbs, "adaptations") and nbs.adaptations:
        pytest.fail("Should not enter this block since adaptations don't exist")


def test_hasattr_impacts_check():
    """Test that hasattr check for impacts works correctly."""
    nbs = NatureBasedSolutionCreate(
        name="Test NBS",
        definition="Test definition",
        cobenefits="Test benefits",
        specificdetails="Test details",
        location="Test location",
    )

    # This should return True since impacts field exists in the schema
    assert hasattr(nbs, "impacts")

    # Even if impacts is None/empty, hasattr should still return True
    assert nbs.impacts is None or len(nbs.impacts) == 0
