import json
import os

import pytest
from pydantic import ValidationError

from nbsapi.schemas.geometry import LineStringGeometry, PointGeometry, PolygonGeometry
from nbsapi.schemas.impact import ImpactIntensity, ImpactUnit
from nbsapi.schemas.physical_properties import PhysicalProperties
from nbsapi.schemas.project import (
    MapSettings,
    ProjectBase,
    ProjectSettings,
)
from nbsapi.schemas.specialized_impacts import (
    ClimateImpact,
    CostImpact,
    EnhancedImpactBase,
    SpecializedImpacts,
    WaterQualityImpact,
)
from nbsapi.schemas.styling import StylingProperties

VOTRIS_DATA_PATH = os.path.join(os.path.dirname(__file__), "fixtures", "votris.json")
with open(VOTRIS_DATA_PATH) as f:
    VOTRIS_DATA = json.load(f)

# Extract a sample area from Votris data
SAMPLE_AREA = VOTRIS_DATA["areas"][0]


# Tests for GeoJSON geometry schemas
def test_point_geometry():
    """Test the PointGeometry schema"""
    # Valid point
    point = PointGeometry(type="Point", coordinates=[4.9041, 52.3676])
    assert point.type == "Point"
    assert point.coordinates == [4.9041, 52.3676]

    # Invalid coordinates (out of range)
    with pytest.raises(ValidationError):
        PointGeometry(type="Point", coordinates=[200, 100])


def test_linestring_geometry():
    """Test the LineStringGeometry schema"""
    # Valid linestring
    linestring = LineStringGeometry(
        type="LineString", coordinates=[[4.9041, 52.3676], [4.9042, 52.3677]]
    )
    assert linestring.type == "LineString"
    assert len(linestring.coordinates) == 2

    # Invalid linestring (not enough points)
    with pytest.raises(ValidationError):
        LineStringGeometry(type="LineString", coordinates=[[4.9041, 52.3676]])


def test_polygon_geometry():
    """Test the PolygonGeometry schema"""
    # Valid polygon (closed)
    polygon = PolygonGeometry(
        type="Polygon",
        coordinates=[
            [[4.9041, 52.3676], [4.9042, 52.3677], [4.9043, 52.3678], [4.9041, 52.3676]]
        ],
    )
    assert polygon.type == "Polygon"
    assert len(polygon.coordinates[0]) == 4

    # Invalid polygon (not closed)
    with pytest.raises(ValidationError):
        PolygonGeometry(
            type="Polygon",
            coordinates=[[[4.9041, 52.3676], [4.9042, 52.3677], [4.9043, 52.3678]]],
        )


# Tests for styling properties
def test_styling_properties():
    """Test the StylingProperties schema"""
    styling = StylingProperties(
        color=SAMPLE_AREA["properties"]["color"],
        hidden=SAMPLE_AREA["properties"]["hidden"],
    )
    assert styling.color == SAMPLE_AREA["properties"]["color"]
    assert styling.hidden == SAMPLE_AREA["properties"]["hidden"]


# Tests for physical properties
def test_physical_properties():
    """Test the PhysicalProperties schema"""
    physical = PhysicalProperties(
        default_inflow=SAMPLE_AREA["properties"]["defaultInflow"],
        default_depth=SAMPLE_AREA["properties"]["defaultDepth"],
        default_width=SAMPLE_AREA["properties"]["defaultWidth"],
    )
    assert physical.default_inflow == SAMPLE_AREA["properties"]["defaultInflow"]
    assert physical.default_depth == SAMPLE_AREA["properties"]["defaultDepth"]
    assert physical.default_width == SAMPLE_AREA["properties"]["defaultWidth"]


# Tests for specialized impacts
def test_climate_impact():
    """Test the ClimateImpact schema"""
    api_data = SAMPLE_AREA["properties"]["apiData"]
    climate = ClimateImpact(
        temp_reduction=api_data["tempReduction"],
        cool_spot=api_data["coolSpot"],
        evapotranspiration=api_data["evapotranspiration"],
    )
    assert climate.temp_reduction == api_data["tempReduction"]
    assert climate.cool_spot == api_data["coolSpot"]
    assert climate.evapotranspiration == api_data["evapotranspiration"]


def test_water_quality_impact():
    """Test the WaterQualityImpact schema"""
    api_data = SAMPLE_AREA["properties"]["apiData"]
    water = WaterQualityImpact(
        capture_unit=api_data["captureUnit"],
        filtering_unit=api_data["filteringUnit"],
        settling_unit=api_data["settlingUnit"],
    )
    assert water.capture_unit == api_data["captureUnit"]
    assert water.filtering_unit == api_data["filteringUnit"]
    assert water.settling_unit == api_data["settlingUnit"]


def test_cost_impact():
    """Test the CostImpact schema"""
    api_data = SAMPLE_AREA["properties"]["apiData"]
    cost = CostImpact(
        construction_cost=api_data["constructionCost"],
        maintenance_cost=api_data["maintenanceCost"],
        currency="EUR",
    )
    assert cost.construction_cost == api_data["constructionCost"]
    assert cost.maintenance_cost == api_data["maintenanceCost"]
    assert cost.currency == "EUR"


def test_specialized_impacts():
    """Test the SpecializedImpacts schema"""
    api_data = SAMPLE_AREA["properties"]["apiData"]
    specialized = SpecializedImpacts(
        climate=ClimateImpact(
            temp_reduction=api_data["tempReduction"], cool_spot=api_data["coolSpot"]
        ),
        water_quality=WaterQualityImpact(filtering_unit=api_data["filteringUnit"]),
        cost=CostImpact(construction_cost=api_data["constructionCost"]),
    )
    assert specialized.climate is not None
    assert specialized.water_quality is not None
    assert specialized.cost is not None
    assert specialized.climate.temp_reduction == api_data["tempReduction"]


def test_enhanced_impact_base():
    """Test the EnhancedImpactBase schema"""
    api_data = SAMPLE_AREA["properties"]["apiData"]
    impact = EnhancedImpactBase(
        magnitude=10.5,
        unit=ImpactUnit(unit="m2", description="area"),
        intensity=ImpactIntensity(intensity="medium"),
        specialized=SpecializedImpacts(
            climate=ClimateImpact(temp_reduction=api_data["tempReduction"])
        ),
    )
    assert impact.magnitude == 10.5
    assert impact.unit.unit == "m2"
    assert impact.intensity.intensity == "medium"
    assert impact.specialized is not None
    assert impact.specialized.climate is not None
    assert impact.specialized.climate.temp_reduction == api_data["tempReduction"]


# Tests for project schemas
def test_project_settings():
    """Test the ProjectSettings schema"""
    settings = ProjectSettings(
        scenario_name="Test Scenario",
        capacity={"heatCoping": True, "floodCoping": True},
        multifunctionality="high",
    )
    assert settings.scenario_name == "Test Scenario"
    assert settings.capacity["heatCoping"] is True
    assert settings.multifunctionality == "high"


def test_project_base():
    """Test the ProjectBase schema"""
    project = ProjectBase(
        title="Test Project",
        description="A test project",
        settings=ProjectSettings(scenario_name="Test Scenario"),
        map=MapSettings(center=[4.9041, 52.3676], zoom=12),
    )
    assert project.title == "Test Project"
    assert project.description == "A test project"
    assert project.settings is not None
    assert project.settings.scenario_name == "Test Scenario"
    assert project.map is not None
    assert project.map.center == [4.9041, 52.3676]
