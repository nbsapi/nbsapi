from pydantic import BaseModel, ConfigDict, Field

# AdaptationTargets are deprecated in v2 - use specialized impacts instead
from nbsapi.schemas.geometry import GeoJSONGeometry
from nbsapi.schemas.impact import ImpactBase
from nbsapi.schemas.physical_properties import PhysicalProperties
from nbsapi.schemas.styling import StylingProperties


class NatureBasedSolutionBase(BaseModel):
    name: str = Field(..., examples=["Coastal Restoration", "Area-1", "Rain Garden"])
    definition: str = Field(
        ..., examples=["Definition of the solution", "Imported from Deltares format"]
    )
    cobenefits: str = Field(
        ..., examples=["Improved biodiversity", "Various environmental benefits"]
    )
    specificdetails: str = Field(
        ..., examples=["Detailed information", "Details from Deltares import"]
    )
    location: str = Field(
        ..., examples=["Coastal Area X", "Imported location", "Urban plaza"]
    )
    geometry: GeoJSONGeometry | None = Field(
        None,
        description="GeoJSON geometry representing the solution's location",
        examples=[
            {
                "type": "Polygon",
                "coordinates": [
                    [
                        [23.717992514920383, 38.00993916350677],
                        [23.71835238960557, 38.00987732368668],
                        [23.718232201749544, 38.009469169435704],
                        [23.718133541363812, 38.00911729628717],
                        [23.717763276983078, 38.009161267544044],
                        [23.717992514920383, 38.00993916350677],
                    ]
                ],
            },
            {
                "type": "LineString",
                "coordinates": [
                    [23.716148279378956, 38.00875382311804],
                    [23.71725307258484, 38.00937559547941],
                    [23.71789424721402, 38.00984192129033],
                ],
            },
            {"type": "Point", "coordinates": [23.71905028688252, 38.009586258632595]},
        ],
    )
    styling: StylingProperties | None = Field(
        None,
        description="Visual styling properties for rendering",
        examples=[
            {"color": "#cfdd20", "hidden": False},
            {"color": "#31D336", "hidden": False},
            {"color": "#DB14D4", "hidden": False},
        ],
    )
    physical_properties: PhysicalProperties | None = Field(
        None,
        description="Physical dimensions and properties of the solution",
        examples=[
            {
                "default_inflow": 1,
                "default_depth": 0.05,
                "default_width": 5,
                "default_radius": 1,
                "area_depth": 0.05,
            },
            {
                "default_inflow": 10,
                "default_depth": 0.35,
                "default_width": 1,
                "default_radius": 0.0001,
            },
        ],
    )
    area: float | None = Field(
        None,
        description="Calculated area in square meters (for polygons)",
        examples=[3672.3235347681, 1686.7294955304058],
    )
    length: float | None = Field(
        None,
        description="Calculated length in meters (for LineString geometries)",
        examples=[133.4385512785903],
    )
    measure_id: str | None = Field(
        None,
        description="Reference to measure type ID (e.g., 6=Bioswale, 8=Detention pond, 12=Green roof, 15=Permeable pavement, 25=Urban forest, 26=Wetland, 33=Underground storage, 37=Infiltration well, 39=Rain garden, 40=Retention pond, 41=Large detention basin, 45=Green corridor)",
        examples=["39", "26", "6", "25", "33"],
    )
    impacts: list[ImpactBase] = Field(
        default_factory=list,
        description="The adaptation impact",
        examples=[
            [
                {
                    "magnitude": 10.5,
                    "unit": {"unit": "m2", "description": "shade"},
                    "intensity": {"intensity": "low"},
                }
            ],
            [
                {
                    "magnitude": 142.33955129172907,
                    "unit": {"unit": "m3", "description": "storage capacity"},
                    "intensity": {"intensity": "high"},
                }
            ],
            [
                {
                    "magnitude": 68.38913509542978,
                    "unit": {"unit": "m3", "description": "storage capacity"},
                    "intensity": {"intensity": "low"},
                }
            ],
        ],
    )


class NatureBasedSolutionCreate(NatureBasedSolutionBase):
    # Note: Adaptation targets are deprecated in v2
    # Use specialized impacts instead for quantitative metrics
    pass

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "name": "Area-1",
                    "definition": "Imported from Deltares format",
                    "cobenefits": "Various environmental benefits",
                    "specificdetails": "Details from Deltares import",
                    "location": "Imported location",
                    "geometry": {
                        "type": "Polygon",
                        "coordinates": [
                            [
                                [23.717992514920383, 38.00993916350677],
                                [23.71835238960557, 38.00987732368668],
                                [23.718232201749544, 38.009469169435704],
                                [23.718133541363812, 38.00911729628717],
                                [23.717763276983078, 38.009161267544044],
                                [23.717992514920383, 38.00993916350677],
                            ]
                        ],
                    },
                    "styling": {"color": "#cfdd20", "hidden": False},
                    "physical_properties": {
                        "default_inflow": 1,
                        "default_depth": 0.05,
                        "default_width": 5,
                        "default_radius": 1,
                        "area_depth": 0.05,
                    },
                    "measure_id": "39",
                    "area": 3672.3235347681,
                    "impacts": [
                        {
                            "magnitude": 10.0,
                            "unit": {"unit": "m2", "description": "area"},
                            "intensity": {"intensity": "medium"},
                        }
                    ],
                },
                {
                    "name": "Area-4",
                    "definition": "Bioswale for water management",
                    "cobenefits": "Water filtration and habitat creation",
                    "specificdetails": "Linear bioswale along roadway",
                    "location": "Street drainage system",
                    "geometry": {
                        "type": "LineString",
                        "coordinates": [
                            [23.716148279378956, 38.00875382311804],
                            [23.71725307258484, 38.00937559547941],
                            [23.71789424721402, 38.00984192129033],
                        ],
                    },
                    "styling": {"color": "#31D336", "hidden": False},
                    "physical_properties": {
                        "default_inflow": 10,
                        "default_depth": 0.35,
                        "default_width": 1,
                        "default_radius": 0.0001,
                    },
                    "measure_id": "6",
                    "impacts": [
                        {
                            "magnitude": 68.38913509542978,
                            "unit": {"unit": "m3", "description": "storage capacity"},
                            "intensity": {"intensity": "low"},
                        }
                    ],
                },
                {
                    "name": "Area-22",
                    "definition": "Infiltration well for groundwater recharge",
                    "cobenefits": "Groundwater replenishment",
                    "specificdetails": "Deep infiltration well",
                    "location": "Urban plaza",
                    "geometry": {
                        "type": "Point",
                        "coordinates": [23.71905028688252, 38.009586258632595],
                    },
                    "styling": {"color": "#DB14D4", "hidden": False},
                    "physical_properties": {
                        "default_inflow": 20,
                        "default_depth": 1,
                        "default_width": 1,
                        "default_radius": 1,
                    },
                    "measure_id": "37",
                    "impacts": [
                        {
                            "magnitude": 3.141592653589793,
                            "unit": {"unit": "m3", "description": "storage capacity"},
                            "intensity": {"intensity": "low"},
                        }
                    ],
                },
            ]
        }
    )


class NatureBasedSolutionUpdate(BaseModel):
    name: str | None = Field(None, examples=["Riprap"])
    definition: str | None = Field(None, examples=["Updated definition"])
    cobenefits: str | None = Field(None, examples=["Enhanced ecosystem services"])
    specificdetails: str | None = Field(None, examples=["Updated detailed information"])
    location: str | None = Field(None, examples=["Updated Coastal Area Y"])
    geometry: GeoJSONGeometry | None = Field(
        None,
        description="GeoJSON geometry representing the solution's location",
    )
    styling: StylingProperties | None = Field(
        None,
        description="Visual styling properties for rendering",
    )
    physical_properties: PhysicalProperties | None = Field(
        None,
        description="Physical dimensions and properties of the solution",
    )
    # Note: Adaptation targets are deprecated in v2
    # Use specialized impacts instead for quantitative metrics


class NatureBasedSolutionRead(NatureBasedSolutionBase):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)
    id: int
    # Note: solution_targets (adaptation targets) are deprecated in v2
    # Use specialized impacts instead for quantitative metrics
