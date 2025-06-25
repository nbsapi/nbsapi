"""Test full round-trip compatibility with Deltares format."""

import json
import os
from typing import Any

import pytest

from nbsapi.schemas.deltares import (
    DeltaresProjectExport,
    DeltaresFeature,
    DeltaresApiData,
)
from nbsapi.schemas.naturebasedsolution import NatureBasedSolutionCreate
from nbsapi.schemas.styling import StylingProperties
from nbsapi.schemas.physical_properties import PhysicalProperties
from nbsapi.schemas.impact import ImpactBase, ImpactUnit, ImpactIntensity
from nbsapi.utils.deltares_converter import (
    convert_solution_to_deltares_feature,
)


# Load Deltares test data (formerly Votris)
DELTARES_DATA_PATH = os.path.join(
    os.path.dirname(__file__), "fixtures", "deltares.json"
)
with open(DELTARES_DATA_PATH) as f:
    DELTARES_DATA = json.load(f)


def convert_deltares_to_api_solution(
    deltares_area: dict[str, Any],
) -> NatureBasedSolutionCreate:
    """Convert a Deltares area to an API v2 NatureBasedSolution."""
    props = deltares_area["properties"]
    # api_data = props["apiData"]  # Not currently used in basic test

    # Note: specialized impacts would be created here if needed
    # Currently using basic impacts for testing

    # Create impacts with specialized data
    impacts = [
        ImpactBase(
            magnitude=10.0,  # Default magnitude
            unit=ImpactUnit(unit="m2", description="area"),
            intensity=ImpactIntensity(intensity="medium"),
        )
    ]

    # Create styling
    styling = StylingProperties(
        color=props.get("color", "#3388ff"),
        hidden=props.get("hidden", False),
    )

    # Create physical properties
    physical_properties = PhysicalProperties(
        default_inflow=props.get("defaultInflow"),
        default_depth=props.get("defaultDepth"),
        default_width=props.get("defaultWidth"),
        default_radius=props.get("defaultRadius"),
        area_inflow=props.get("areaInflow"),
        area_depth=props.get("areaDepth"),
        area_width=props.get("areaWidth"),
        area_radius=props.get("areaRadius"),
    )

    return NatureBasedSolutionCreate(
        name=props["name"],
        definition="Imported from Deltares format",
        cobenefits="Various environmental benefits",
        specificdetails="Details from Deltares import",
        location="Imported location",
        geometry=deltares_area["geometry"],
        styling=styling,
        physical_properties=physical_properties,
        measure_id=props["measure"],
        area=props.get("area"),
        length=props.get("length"),
        impacts=impacts,
        # Note: adaptations (adaptation targets) are deprecated in v2
        # Use specialized impacts instead for quantitative metrics
    )


def test_deltares_project_import():
    """Test that we can import the complete Deltares project structure."""
    # Validate that the loaded data conforms to our Deltares schema
    deltares_project = DeltaresProjectExport(**DELTARES_DATA)

    # Check that all areas are valid features
    assert len(deltares_project.areas) > 0
    assert all(isinstance(area, DeltaresFeature) for area in deltares_project.areas)

    # Check that all required fields are present
    assert deltares_project.settings is not None
    assert deltares_project.map is not None
    assert deltares_project.settings.projectArea is not None
    assert deltares_project.settings.targets is not None


@pytest.mark.parametrize("area_index", range(min(5, len(DELTARES_DATA["areas"]))))
def test_deltares_area_to_solution_conversion(area_index):
    """Test converting individual Deltares areas to API solutions."""
    deltares_area = DELTARES_DATA["areas"][area_index]

    # Convert to API solution
    api_solution = convert_deltares_to_api_solution(deltares_area)

    # Validate the conversion
    assert api_solution.name == deltares_area["properties"]["name"]
    assert api_solution.measure_id == deltares_area["properties"]["measure"]
    assert api_solution.geometry is not None
    assert api_solution.styling is not None
    assert api_solution.physical_properties is not None

    # Check that geometry type is preserved
    assert api_solution.geometry.type == deltares_area["geometry"]["type"]
    assert api_solution.geometry.coordinates == deltares_area["geometry"]["coordinates"]


def test_solution_to_deltares_conversion():
    """Test converting an API solution back to Deltares format."""
    # Use the first area from test data
    original_deltares = DELTARES_DATA["areas"][0]

    # Convert to API solution
    api_solution = convert_deltares_to_api_solution(original_deltares)

    # Mock the solution with an ID (as it would have after DB save)
    api_solution_with_id = type(
        "MockSolution",
        (),
        {
            **api_solution.model_dump(),
            "id": 1,
            "impacts": [],  # Start with empty impacts for this test
        },
    )()

    # Convert back to Deltares
    deltares_feature = convert_solution_to_deltares_feature(api_solution_with_id)

    # Check critical fields are preserved
    assert deltares_feature.properties.name == original_deltares["properties"]["name"]
    assert (
        deltares_feature.properties.measure
        == original_deltares["properties"]["measure"]
    )
    assert deltares_feature.properties.color == original_deltares["properties"]["color"]
    assert deltares_feature.geometry["type"] == original_deltares["geometry"]["type"]

    # Check that physical properties are preserved
    original_props = original_deltares["properties"]
    converted_props = deltares_feature.properties

    assert converted_props.defaultInflow == original_props["defaultInflow"]
    assert converted_props.defaultDepth == original_props["defaultDepth"]
    assert converted_props.defaultWidth == original_props["defaultWidth"]
    assert converted_props.defaultRadius == original_props["defaultRadius"]


def test_deltares_api_data_structure():
    """Test that the Deltares API data structure matches expected format."""
    for area in DELTARES_DATA["areas"]:
        api_data = area["properties"]["apiData"]

        # Validate that all expected fields exist
        deltares_api_data = DeltaresApiData(**api_data)

        # Check that all fields are properly typed
        assert isinstance(deltares_api_data.constructionCost, int | float)
        assert isinstance(deltares_api_data.maintenanceCost, int | float)
        assert isinstance(deltares_api_data.tempReduction, int | float)
        assert isinstance(deltares_api_data.storageCapacity, int | float)

        # Check camelCase field names are preserved
        assert hasattr(deltares_api_data, "constructionCost")
        assert hasattr(deltares_api_data, "maintenanceCost")
        assert hasattr(deltares_api_data, "tempReduction")
        assert hasattr(deltares_api_data, "coolSpot")
        assert hasattr(deltares_api_data, "captureUnit")
        assert hasattr(deltares_api_data, "filteringUnit")
        assert hasattr(deltares_api_data, "settlingUnit")
        assert hasattr(deltares_api_data, "groundwater_recharge")
        assert hasattr(deltares_api_data, "evapotranspiration")
        assert hasattr(deltares_api_data, "storageCapacity")


def test_deltares_geometry_types():
    """Test that all geometry types in Deltares data are supported."""
    geometry_types = set()

    for area in DELTARES_DATA["areas"]:
        geom_type = area["geometry"]["type"]
        geometry_types.add(geom_type)

        # Validate each geometry
        geometry = area["geometry"]
        assert "type" in geometry
        assert "coordinates" in geometry

        # Check coordinate structure based on type
        if geom_type == "Point":
            assert len(geometry["coordinates"]) >= 2
        elif geom_type == "LineString":
            assert len(geometry["coordinates"]) >= 2
            assert all(len(coord) >= 2 for coord in geometry["coordinates"])
        elif geom_type == "Polygon":
            assert len(geometry["coordinates"]) >= 1
            assert all(len(ring) >= 4 for ring in geometry["coordinates"])

    # Ensure we have multiple geometry types in our test data
    assert len(geometry_types) > 1, "Test data should include multiple geometry types"
    assert (
        "Point" in geometry_types
        or "LineString" in geometry_types
        or "Polygon" in geometry_types
    )


def test_deltares_measure_types():
    """Test that all measure types in Deltares data are properly identified."""
    measure_types = set()

    for area in DELTARES_DATA["areas"]:
        measure_id = area["properties"]["measure"]
        measure_types.add(measure_id)

        # Validate measure ID format
        assert isinstance(measure_id, str)
        assert len(measure_id) > 0

    # Check that we have multiple measure types
    assert len(measure_types) > 1, "Test data should include multiple measure types"

    # Check measure overrides exist for these types
    measure_overrides = DELTARES_DATA.get("measureOverrides", {})
    for measure_id in measure_types:
        # Some measures should have overrides, but not all necessarily
        if measure_id in measure_overrides:
            assert "color" in measure_overrides[measure_id]
            assert "hex" in measure_overrides[measure_id]["color"]


def test_deltares_project_settings():
    """Test that project settings are properly structured."""
    settings = DELTARES_DATA["settings"]

    # Check required top-level settings
    assert "area" in settings
    assert "general" in settings
    assert "projectArea" in settings
    assert "targets" in settings

    # Check project area settings
    project_area = settings["projectArea"]
    assert "scenarioName" in project_area
    assert "capacity" in project_area
    assert "multifunctionality" in project_area
    assert "scale" in project_area
    assert "suitability" in project_area

    # Check targets structure
    targets = settings["targets"]
    assert "climate" in targets
    assert "cost" in targets
    assert "waterquality" in targets

    # Check that each target category has proper structure
    for target_category in targets.values():
        for target_config in target_category.values():
            assert "include" in target_config
            assert "value" in target_config
            assert isinstance(target_config["include"], bool)
            assert isinstance(target_config["value"], str)


def test_complete_roundtrip_compatibility():
    """Test complete round-trip: Deltares -> API -> Deltares with data preservation."""
    original_data = DELTARES_DATA

    # Convert the first few areas to API format
    api_solutions = []
    for area in original_data["areas"][:3]:  # Test with first 3 areas
        api_solution = convert_deltares_to_api_solution(area)
        api_solutions.append(api_solution)

    # Mock solutions with IDs as they would have after database storage
    mock_solutions = []
    for i, solution in enumerate(api_solutions):
        mock_solution = type(
            "MockSolution",
            (),
            {
                **solution.model_dump(),
                "id": i + 1,
                "impacts": [],  # Empty impacts for this test
            },
        )()
        mock_solutions.append(mock_solution)

    # Convert back to Deltares features
    deltares_features = [
        convert_solution_to_deltares_feature(solution) for solution in mock_solutions
    ]

    # Check that critical data is preserved
    for original_area, converted_feature in zip(
        original_data["areas"][:3], deltares_features
    ):
        original_props = original_area["properties"]
        converted_props = converted_feature.properties

        # Check basic properties
        assert converted_props.name == original_props["name"]
        assert converted_props.measure == original_props["measure"]
        assert converted_props.color == original_props["color"]
        assert converted_props.hidden == original_props["hidden"]

        # Check physical properties
        assert converted_props.defaultInflow == original_props["defaultInflow"]
        assert converted_props.defaultDepth == original_props["defaultDepth"]
        assert converted_props.defaultWidth == original_props["defaultWidth"]
        assert converted_props.defaultRadius == original_props["defaultRadius"]

        # Check geometry preservation
        assert converted_feature.geometry["type"] == original_area["geometry"]["type"]
        assert (
            converted_feature.geometry["coordinates"]
            == original_area["geometry"]["coordinates"]
        )


def test_deltares_field_naming_conventions():
    """Test that Deltares uses proper camelCase field naming."""
    # Check areas use camelCase
    for area in DELTARES_DATA["areas"]:
        props = area["properties"]
        api_data = props["apiData"]

        # These should be camelCase
        camel_case_fields = [
            "constructionCost",
            "maintenanceCost",
            "tempReduction",
            "coolSpot",
            "captureUnit",
            "filteringUnit",
            "settlingUnit",
            "storageCapacity",
            "evapotranspiration",
            "defaultInflow",
            "defaultDepth",
            "defaultWidth",
            "defaultRadius",
            "areaInflow",
            "areaDepth",
            "areaWidth",
            "areaRadius",
        ]

        for field in camel_case_fields:
            if field in props or field in api_data:
                # Field exists and is camelCase
                assert field[0].islower(), f"Field {field} should start with lowercase"
                # Should not contain underscores
                assert "_" not in field, f"Field {field} should not contain underscores"

    # Check that settings use camelCase where appropriate
    settings = DELTARES_DATA["settings"]["projectArea"]
    camel_case_settings = ["scenarioName", "multifunctionality"]

    for field in camel_case_settings:
        if field in settings:
            assert field[0].islower(), f"Setting {field} should start with lowercase"
