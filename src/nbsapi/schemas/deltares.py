"""Deltares export format schemas for compatibility with Deltares API."""

from typing import Any, Literal
from pydantic import BaseModel, Field


class DeltaresApiData(BaseModel):
    """API data in Deltares format with camelCase field names."""

    constructionCost: float = Field(0.0, description="Construction cost")
    maintenanceCost: float = Field(0.0, description="Annual maintenance cost")
    coolSpot: float = Field(0.0, description="Cool spot metric")
    tempReduction: float = Field(
        0.0, description="Temperature reduction in degrees Celsius"
    )
    captureUnit: float = Field(0.0, description="Water capture unit metric")
    filteringUnit: float = Field(0.0, description="Water filtering unit metric")
    settlingUnit: float = Field(0.0, description="Water settling unit metric")
    Fmeas_area: float = Field(0.0, description="Measured area metric")
    groundwater_recharge: float = Field(
        0.0, description="Groundwater recharge in mm/day"
    )
    evapotranspiration: float = Field(0.0, description="Evapotranspiration in mm/day")
    storageCapacity: float = Field(
        0.0, description="Water storage capacity in cubic meters"
    )


class DeltaresProperties(BaseModel):
    """Properties for a Deltares feature."""

    name: str = Field(..., description="Name of the area")
    hidden: bool = Field(False, description="Whether the feature is hidden")
    apiData: DeltaresApiData = Field(..., description="Impact and performance data")
    measure: str = Field(..., description="Measure type ID")
    color: str = Field(..., description="Hex color code for rendering")
    defaultInflow: float = Field(..., description="Default inflow rate")
    defaultDepth: float = Field(..., description="Default depth in meters")
    defaultWidth: float = Field(..., description="Default width in meters")
    defaultRadius: float = Field(..., description="Default radius in meters")
    areaInflow: float | None = Field(None, description="Area-specific inflow")
    areaDepth: str | None = Field(None, description="Area-specific depth")
    areaWidth: float | None = Field(None, description="Area-specific width")
    areaRadius: float | None = Field(None, description="Area-specific radius")
    area: float | None = Field(None, description="Calculated area in square meters")
    length: float | None = Field(None, description="Calculated length in meters")


class DeltaresFeature(BaseModel):
    """GeoJSON Feature in Deltares format."""

    id: str = Field(..., description="Feature ID")
    type: Literal["Feature"] = "Feature"
    properties: DeltaresProperties
    geometry: dict[str, Any] = Field(..., description="GeoJSON geometry")


class DeltaresProjectArea(BaseModel):
    """Project area configuration in Deltares format."""

    scenarioName: str = Field(..., description="Scenario name")
    capacity: dict[str, bool] = Field(..., description="Coping capacities")
    multifunctionality: str = Field(..., description="Multifunctionality level")
    scale: dict[str, bool] = Field(..., description="Scale settings")
    suitability: dict[str, bool] = Field(..., description="Space suitability")
    subsurface: str = Field(..., description="Subsurface type")
    surface: str = Field(..., description="Surface type")
    soil: str = Field(..., description="Soil type")
    slope: str = Field(..., description="Terrain slope")


class DeltaresTargetValue(BaseModel):
    """Target value with inclusion flag."""

    include: bool = Field(True, description="Whether to include in calculations")
    value: str = Field(..., description="Target value (string for formulas)")


class DeltaresClimateTargets(BaseModel):
    """Climate targets in Deltares format."""

    storageCapacity: DeltaresTargetValue | None = None
    groundwater_recharge: DeltaresTargetValue | None = None
    evapotranspiration: DeltaresTargetValue | None = None
    tempReduction: DeltaresTargetValue | None = None
    coolSpot: DeltaresTargetValue | None = None
    Fmeas_area: DeltaresTargetValue | None = None


class DeltaresCostTargets(BaseModel):
    """Cost targets in Deltares format."""

    constructionCost: DeltaresTargetValue | None = None
    maintenanceCost: DeltaresTargetValue | None = None


class DeltaresWaterQualityTargets(BaseModel):
    """Water quality targets in Deltares format."""

    filteringUnit: DeltaresTargetValue | None = None
    captureUnit: DeltaresTargetValue | None = None
    settlingUnit: DeltaresTargetValue | None = None


class DeltaresTargets(BaseModel):
    """All targets in Deltares format."""

    climate: DeltaresClimateTargets | None = None
    cost: DeltaresCostTargets | None = None
    waterquality: DeltaresWaterQualityTargets | None = None


class DeltaresMapSettings(BaseModel):
    """Map settings in Deltares format."""

    center: dict[str, float] = Field(..., description="Map center with lat/lng")
    zoom: float = Field(..., description="Map zoom level")
    customLayers: list[Any] = Field(default_factory=list)
    layers: list[dict[str, Any]] = Field(default_factory=list)


class DeltaresSettings(BaseModel):
    """Project settings in Deltares format."""

    area: dict[str, Any] = Field(..., description="Project area boundary")
    general: dict[str, str] = Field(..., description="General settings")
    projectArea: DeltaresProjectArea = Field(
        ..., description="Project area configuration"
    )
    targets: DeltaresTargets = Field(..., description="Project targets")
    userViewedProjectSettings: bool = Field(True)
    pluvfloodParam: dict[str, float] | None = None


class DeltaresProjectExport(BaseModel):
    """Complete project export in Deltares format."""

    areas: list[DeltaresFeature] = Field(
        ..., description="List of NBS areas as GeoJSON features"
    )
    legalAccepted: bool = Field(True)
    map: DeltaresMapSettings = Field(..., description="Map configuration")
    displayMap: bool = Field(True)
    settings: DeltaresSettings = Field(..., description="Project settings")
    measureOverrides: dict[str, dict[str, Any]] = Field(
        default_factory=dict, description="Measure type overrides"
    )
    savedInWorkspace: str | None = Field(None, description="Workspace identifier")
