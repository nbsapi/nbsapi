"""Test the create solution impact endpoint."""

from nbsapi.schemas.specialized_impacts import EnhancedImpactBase


def test_enhanced_impact_can_be_serialized():
    """Test that EnhancedImpactBase can be serialized to JSON."""
    impact_data = EnhancedImpactBase(
        magnitude=142.33955129172907,
        unit={"unit": "m3", "description": "storage capacity"},
        intensity={"intensity": "high"},
        specialized={
            "climate": {
                "temp_reduction": 0.05763750310256802,
                "cool_spot": 0,
                "evapotranspiration": 0.04105408115726775,
                "groundwater_recharge": -0.04348092339316535,
                "storage_capacity": 142.33955129172907,
            }
        },
    )

    # Test that it can be converted to dict (which FastAPI does for JSON serialization)
    impact_dict = impact_data.model_dump()
    assert "magnitude" in impact_dict
    assert "unit" in impact_dict
    assert "intensity" in impact_dict
    assert "specialized" in impact_dict

    # Test that specialized data is properly nested
    assert "climate" in impact_dict["specialized"]
    assert "temp_reduction" in impact_dict["specialized"]["climate"]


def test_enhanced_impact_with_minimal_data():
    """Test EnhancedImpactBase with only required fields."""
    impact_data = EnhancedImpactBase(
        magnitude=100.0,
        unit={"unit": "m2", "description": "area"},
        intensity={"intensity": "low"},
    )

    # Should not raise any validation errors
    assert impact_data.magnitude == 100.0
    assert impact_data.unit.unit == "m2"
    assert impact_data.intensity.intensity == "low"
    assert impact_data.specialized is None

    # Should be serializable
    impact_dict = impact_data.model_dump()
    assert impact_dict["specialized"] is None
