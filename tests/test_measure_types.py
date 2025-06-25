"""Test measure types functionality."""

import pytest
from pydantic import ValidationError

from nbsapi.schemas.measure_type import (
    MeasureTypeCreate,
    MeasureTypeRead,
    MeasureTypeUpdate,
)


def test_measure_type_create():
    """Test creating a measure type."""
    measure_type = MeasureTypeCreate(
        id="39",
        name="Green Roof",
        description="Vegetated roof system for stormwater management",
        default_color="#31D336",
        default_inflow=1.0,
        default_depth=0.05,
        default_width=5.0,
        default_radius=1.0,
    )

    assert measure_type.id == "39"
    assert measure_type.name == "Green Roof"
    assert measure_type.default_color == "#31D336"
    assert measure_type.default_depth == 0.05


def test_measure_type_read():
    """Test reading a measure type."""
    measure_type = MeasureTypeRead(
        id="26",
        name="Rain Garden",
        description="Bioretention cell for stormwater management",
        default_color="#D19220",
        default_inflow=1.0,
        default_depth=0.1,
        default_width=4.0,
        default_radius=0.0001,
    )

    assert measure_type.id == "26"
    assert measure_type.name == "Rain Garden"
    assert measure_type.default_color == "#D19220"


def test_measure_type_update():
    """Test updating a measure type."""
    measure_type_update = MeasureTypeUpdate(
        name="Updated Green Roof",
        description="Updated description",
        default_color="#32D337",
    )

    assert measure_type_update.name == "Updated Green Roof"
    assert measure_type_update.description == "Updated description"
    assert measure_type_update.default_color == "#32D337"
    assert measure_type_update.default_inflow is None  # Not provided


def test_measure_type_minimal():
    """Test creating a measure type with minimal data."""
    measure_type = MeasureTypeCreate(
        id="simple",
        name="Simple Measure",
    )

    assert measure_type.id == "simple"
    assert measure_type.name == "Simple Measure"
    assert measure_type.description is None
    assert measure_type.default_color is None


def test_measure_type_validation():
    """Test measure type validation."""
    # ID is required
    with pytest.raises(ValidationError):
        MeasureTypeCreate(name="Missing ID")

    # Name is required
    with pytest.raises(ValidationError):
        MeasureTypeCreate(id="1")
