"""Test SQLAlchemy model relationships."""

from nbsapi.models import MeasureType, NatureBasedSolution


def test_measure_type_nbs_relationship_models():
    """Test that NatureBasedSolution and MeasureType models can be instantiated without errors."""
    # Create model instances to test they can be created without relationship errors
    measure_type = MeasureType(
        id="green_roof",
        name="Green Roof",
        description="Vegetated roof system",
        default_color="#31D336",
    )

    # Create a NatureBasedSolution - this should not raise KeyError about MeasureType
    nbs = NatureBasedSolution(
        name="Test Green Roof",
        definition="A test green roof installation",
        cobenefits="Urban cooling, biodiversity",
        specificdetails="Extensive green roof with sedum",
        location="Amsterdam",
        measure_id="green_roof",
    )

    # Test that both models can be created successfully
    assert measure_type.id == "green_roof"
    assert measure_type.name == "Green Roof"
    assert nbs.name == "Test Green Roof"
    assert nbs.measure_id == "green_roof"


def test_models_use_same_base():
    """Test that both models use the same SQLAlchemy Base."""
    assert MeasureType.metadata is NatureBasedSolution.metadata
    assert hasattr(MeasureType, "__tablename__")
    assert hasattr(NatureBasedSolution, "__tablename__")
