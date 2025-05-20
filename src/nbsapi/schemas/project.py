from pydantic import BaseModel, Field, ConfigDict

from nbsapi.schemas.naturebasedsolution import NatureBasedSolutionRead


class ProjectSettings(BaseModel):
    """Project-level settings for NBS projects"""

    scenario_name: str | None = Field(
        None,
        description="Name of the scenario",
        examples=[
            "Urban Heat Island Mitigation",
            "Athens_area_5_Medium_density_mixed_use",
        ],
    )
    capacity: dict[str, bool] | None = Field(
        None,
        description="Capacity settings for different adaptation types",
        examples=[
            {
                "heatCoping": True,
                "droughtCoping": False,
                "floodCoping": True,
                "waterSafetyCoping": False,
            }
        ],
    )
    multifunctionality: str | None = Field(
        None, description="Multifunctionality setting", examples=["high", "1"]
    )
    scale: dict[str, bool] | None = Field(
        None,
        description="Scale settings for the project",
        examples=[
            {"city": True, "neighbourhood": True, "street": False, "building": False}
        ],
    )
    suitability: dict[str, bool] | None = Field(
        None,
        description="Space suitability settings",
        examples=[
            {
                "greySpace": True,
                "greenSpacePrivateGardens": False,
                "greenSpaceNoRecreation": True,
                "greenSpaceRecreationUrbanFarming": True,
                "greyGreenSpaceSportsPlayground": False,
                "redSpace": False,
                "blueSpace": True,
            }
        ],
    )
    subsurface: str | None = Field(
        None, description="Subsurface type", examples=["clay", "high"]
    )
    surface: str | None = Field(
        None, description="Surface type", examples=["paved", "flatRoofs"]
    )
    soil: str | None = Field(None, description="Soil type", examples=["sandy", "sand"])
    slope: str | None = Field(
        None, description="Terrain slope", examples=["flat", "flatAreaHighGround"]
    )


class TargetValue(BaseModel):
    """Target value with inclusion flag"""

    include: bool = Field(
        default=True, description="Whether to include this target in calculations"
    )
    value: str = Field(
        ...,
        description="Target value (string to allow for formulas)",
        examples=["500", "area * 0.2", "1400", "0", "100"],
    )


class ClimateTargets(BaseModel):
    """Climate-related targets for the project"""

    storage_capacity: TargetValue | None = None
    groundwater_recharge: TargetValue | None = None
    evapotranspiration: TargetValue | None = None
    temp_reduction: TargetValue | None = None
    cool_spot: TargetValue | None = None


class CostTargets(BaseModel):
    """Cost-related targets for the project"""

    construction_cost: TargetValue | None = None
    maintenance_cost: TargetValue | None = None


class WaterQualityTargets(BaseModel):
    """Water quality targets for the project"""

    filtering_unit: TargetValue | None = None
    capture_unit: TargetValue | None = None
    settling_unit: TargetValue | None = None


class ProjectTargets(BaseModel):
    """Project-level targets for different impact categories"""

    climate: ClimateTargets | None = None
    cost: CostTargets | None = None
    water_quality: WaterQualityTargets | None = None


class MapSettings(BaseModel):
    """Map display settings for the project"""

    center: list[float] | None = Field(
        None,
        description="Map center coordinates [longitude, latitude]",
        examples=[[4.9041, 52.3676], [23.71841890133385, 38.00910725441946]],
    )
    zoom: int | None = Field(None, description="Map zoom level", examples=[12, 16])
    base_layer: str | None = Field(
        None, description="Base map layer", examples=["OpenStreetMap", "Satellite"]
    )


class ProjectBase(BaseModel):
    """Base schema for NBS projects"""

    model_config = ConfigDict(from_attributes=True)

    title: str = Field(
        ...,
        description="Project title",
        examples=["Urban Heat Island Mitigation Plan", "Votris project area"],
    )
    description: str | None = Field(
        None,
        description="Project description",
        examples=[
            "A comprehensive plan to reduce urban heat island effects in the city center.",
            "Urban nature-based solutions implementation",
        ],
    )
    settings: ProjectSettings | None = Field(None, description="Project settings")
    map: MapSettings | None = Field(None, description="Map display settings")
    targets: ProjectTargets | None = Field(None, description="Project targets")


class ProjectCreate(ProjectBase):
    """Schema for creating a new project"""

    areas: list[int] | None = Field(
        default_factory=list,
        description="List of NBS solution IDs to include in the project",
        examples=[[1, 2, 3]],
    )

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "title": "Votris project area",
                    "description": "Urban nature-based solutions implementation",
                    "settings": {
                        "scenario_name": "Athens_area_5_Medium_density_mixed_use",
                        "capacity": {
                            "heatCoping": True,
                            "droughtCoping": True,
                            "floodCoping": True,
                            "waterSafetyCoping": False,
                        },
                        "multifunctionality": "1",
                        "scale": {
                            "city": False,
                            "neighbourhood": True,
                            "street": True,
                            "building": True,
                        },
                        "suitability": {
                            "greySpace": True,
                            "greenSpacePrivateGardens": True,
                            "greenSpaceNoRecreation": True,
                            "greenSpaceRecreationUrbanFarming": False,
                            "greyGreenSpaceSportsPlayground": True,
                            "redSpace": True,
                            "blueSpace": False,
                        },
                        "subsurface": "high",
                        "surface": "flatRoofs",
                        "soil": "sand",
                        "slope": "flatAreaHighGround",
                    },
                    "map": {
                        "center": [23.71841890133385, 38.00910725441946],
                        "zoom": 16,
                        "base_layer": "OpenStreetMap",
                    },
                    "targets": {
                        "climate": {
                            "storage_capacity": {"include": True, "value": "1400"},
                            "groundwater_recharge": {"include": True, "value": "0"},
                            "evapotranspiration": {"include": True, "value": "0"},
                            "temp_reduction": {"include": True, "value": "0"},
                            "cool_spot": {"include": True, "value": "0"},
                        },
                        "cost": {
                            "construction_cost": {"include": True, "value": "0"},
                            "maintenance_cost": {"include": True, "value": "0"},
                        },
                        "water_quality": {
                            "filtering_unit": {"include": True, "value": "100"},
                            "capture_unit": {"include": True, "value": "100"},
                            "settling_unit": {"include": True, "value": "100"},
                        },
                    },
                    "areas": [1, 2, 3],
                }
            ]
        }
    )


class ProjectRead(ProjectBase):
    """Schema for reading a project with its NBS solutions"""

    id: str = Field(..., description="Project ID", examples=["proj-123"])
    areas: list[NatureBasedSolutionRead] = Field(
        default_factory=list,
        description="List of NBS solutions included in the project",
    )


class ProjectUpdate(BaseModel):
    """Schema for updating a project"""

    title: str | None = Field(
        None,
        description="Project title",
        examples=["Updated Urban Heat Island Mitigation Plan"],
    )
    description: str | None = Field(
        None,
        description="Project description",
        examples=["Updated project description"],
    )
    settings: ProjectSettings | None = Field(None, description="Project settings")
    map: MapSettings | None = Field(None, description="Map display settings")
    targets: ProjectTargets | None = Field(None, description="Project targets")
    areas: list[int] | None = Field(
        None,
        description="List of NBS solution IDs to include in the project",
        examples=[[1, 2, 4, 5]],
    )
