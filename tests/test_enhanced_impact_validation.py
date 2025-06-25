"""Test validation of EnhancedImpactBase schema."""

import pytest
from pydantic import ValidationError

from nbsapi.schemas.specialized_impacts import EnhancedImpactBase
from nbsapi.schemas.impact import ImpactIntensity, ImpactUnit


def test_enhanced_impact_base_valid():
    """Test that valid EnhancedImpactBase can be created."""
    impact_data = {
        "magnitude": 142.33955129172907,
        "unit": {"unit": "m3", "description": "storage capacity"},
        "intensity": {"intensity": "high"},
        "specialized": {
            "climate": {
                "temp_reduction": 0.05763750310256802,
                "cool_spot": 0,
                "evapotranspiration": 0.04105408115726775,
                "groundwater_recharge": -0.04348092339316535,
                "storage_capacity": 142.33955129172907,
            }
        },
    }

    impact = EnhancedImpactBase(**impact_data)
    assert impact.magnitude == 142.33955129172907
    assert impact.unit.unit == "m3"
    assert impact.intensity.intensity == "high"
    assert impact.specialized.climate.temp_reduction == 0.05763750310256802


def test_enhanced_impact_base_missing_required_fields():
    """Test that missing required fields raise ValidationError."""
    # Missing magnitude
    with pytest.raises(ValidationError):
        EnhancedImpactBase(
            unit={"unit": "m3", "description": "storage capacity"},
            intensity={"intensity": "high"},
        )

    # Missing unit
    with pytest.raises(ValidationError):
        EnhancedImpactBase(
            magnitude=142.33955129172907, intensity={"intensity": "high"}
        )

    # Missing intensity
    with pytest.raises(ValidationError):
        EnhancedImpactBase(
            magnitude=142.33955129172907,
            unit={"unit": "m3", "description": "storage capacity"},
        )


def test_enhanced_impact_base_minimal():
    """Test EnhancedImpactBase with minimal required fields."""
    impact = EnhancedImpactBase(
        magnitude=100.0,
        unit={"unit": "m2", "description": "area"},
        intensity={"intensity": "medium"},
    )

    assert impact.magnitude == 100.0
    assert impact.unit.unit == "m2"
    assert impact.intensity.intensity == "medium"
    assert impact.specialized is None


def test_impact_unit_missing_description():
    """Test that ImpactUnit requires description."""
    with pytest.raises(ValidationError):
        ImpactUnit(unit="m3")


def test_impact_intensity_missing_intensity():
    """Test that ImpactIntensity requires intensity."""
    with pytest.raises(ValidationError):
        ImpactIntensity()


def test_nested_objects_validation():
    """Test validation of nested objects within EnhancedImpactBase."""
    # Invalid unit - missing description
    with pytest.raises(ValidationError):
        EnhancedImpactBase(
            magnitude=100.0,
            unit={"unit": "m3"},  # Missing description
            intensity={"intensity": "high"},
        )

    # Invalid intensity - missing intensity field
    with pytest.raises(ValidationError):
        EnhancedImpactBase(
            magnitude=100.0,
            unit={"unit": "m3", "description": "volume"},
            intensity={},  # Missing intensity field
        )
