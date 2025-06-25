from pydantic import BaseModel, ConfigDict, Field

from nbsapi.schemas.impact import ImpactBase


class ClimateImpact(BaseModel):
    """Climate-related impact metrics for nature-based solutions"""

    temp_reduction: float | None = Field(
        None,
        description="Temperature reduction in degrees Celsius",
        examples=[1.5, 0.05763750310256802, 0.017130684163256523],
    )
    cool_spot: float | None = Field(
        None,
        description="Cool spot metric (0 or 1 for presence/absence)",
        examples=[10.0, 0, 1],
    )
    evapotranspiration: float | None = Field(
        None,
        description="Evapotranspiration in mm/day",
        examples=[2.5, 0.04105408115726775, 0.4249194373931119, 1.0834989660542467],
    )
    groundwater_recharge: float | None = Field(
        None,
        description="Groundwater recharge in mm/day (negative values indicate loss)",
        examples=[3.2, -0.04348092339316535, 0.00839806346130099, -0.02213122069755791],
    )
    storage_capacity: float | None = Field(
        None,
        description="Water storage capacity in cubic meters",
        examples=[500.0, 142.33955129172907, 68.38913509542978, 937.3927093499392],
    )

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "temp_reduction": 0.05763750310256802,
                    "cool_spot": 0,
                    "evapotranspiration": 0.04105408115726775,
                    "groundwater_recharge": -0.04348092339316535,
                    "storage_capacity": 142.33955129172907,
                },
                {
                    "temp_reduction": 0.09489452282090556,
                    "cool_spot": 1,
                    "evapotranspiration": 0.0675915373075222,
                    "groundwater_recharge": -0.07158709616313928,
                    "storage_capacity": 937.3927093499392,
                },
            ]
        }
    )


class WaterQualityImpact(BaseModel):
    """Water quality impact metrics for nature-based solutions"""

    capture_unit: float | None = Field(
        None,
        description="Capture unit metric (pollutant capture efficiency)",
        examples=[45.0, -0.2831315941880535, 1.3271781691898368, 0.16648161898404484],
    )
    filtering_unit: float | None = Field(
        None,
        description="Filtering unit metric (filtration efficiency)",
        examples=[78.0, 1.8201316769232005, 1.4930754403385667, 0.9744669425837609],
    )
    settling_unit: float | None = Field(
        None,
        description="Settling unit metric (sedimentation efficiency)",
        examples=[92.0, 1.8403553622223476, 1.4930754403385667, 0.3329632379680897],
    )

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "capture_unit": -0.2831315941880535,
                    "filtering_unit": 1.8201316769232005,
                    "settling_unit": 1.8403553622223476,
                },
                {
                    "capture_unit": 1.3271781691898368,
                    "filtering_unit": 1.4930754403385667,
                    "settling_unit": 1.4930754403385667,
                },
            ]
        }
    )


class CostImpact(BaseModel):
    """Cost-related metrics for nature-based solutions"""

    construction_cost: float | None = Field(
        None,
        description="Construction cost in currency units",
        examples=[5000.0, 0, 58381.40474038341, 211526.67671768225],
    )
    maintenance_cost: float | None = Field(
        None,
        description="Annual maintenance cost in currency units",
        examples=[500.0, 0, 245.20189990961032, 12691.600603060935],
    )
    currency: str | None = Field(
        "EUR", description="Currency code", examples=["EUR", "USD", "GBP"]
    )

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "construction_cost": 58381.40474038341,
                    "maintenance_cost": 245.20189990961032,
                    "currency": "EUR",
                },
                {
                    "construction_cost": 211526.67671768225,
                    "maintenance_cost": 12691.600603060935,
                    "currency": "EUR",
                },
            ]
        }
    )


class SpecializedImpacts(BaseModel):
    """Container for all specialized impact types"""

    climate: ClimateImpact | None = Field(None, description="Climate-related impacts")
    water_quality: WaterQualityImpact | None = Field(
        None, description="Water quality impacts"
    )
    cost: CostImpact | None = Field(None, description="Cost-related impacts")

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "climate": {
                        "temp_reduction": 0.05763750310256802,
                        "cool_spot": 0,
                        "evapotranspiration": 0.04105408115726775,
                        "groundwater_recharge": -0.04348092339316535,
                        "storage_capacity": 142.33955129172907,
                    }
                },
                {
                    "water_quality": {
                        "capture_unit": -0.2831315941880535,
                        "filtering_unit": 1.8201316769232005,
                        "settling_unit": 1.8403553622223476,
                    }
                },
                {
                    "cost": {
                        "construction_cost": 58381.40474038341,
                        "maintenance_cost": 245.20189990961032,
                        "currency": "EUR",
                    }
                },
            ]
        }
    )


class EnhancedImpactBase(ImpactBase):
    """Enhanced version of ImpactBase that includes specialized impacts"""

    specialized: SpecializedImpacts | None = Field(
        None, description="Specialized impact metrics by category"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
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
                },
                {
                    "magnitude": 1.8201316769232005,
                    "unit": {
                        "unit": "units",
                        "description": "water quality improvement",
                    },
                    "intensity": {"intensity": "medium"},
                    "specialized": {
                        "water_quality": {
                            "capture_unit": -0.2831315941880535,
                            "filtering_unit": 1.8201316769232005,
                            "settling_unit": 1.8403553622223476,
                        }
                    },
                },
                {
                    "magnitude": 58381.40474038341,
                    "unit": {"unit": "EUR", "description": "construction cost"},
                    "intensity": {"intensity": "high"},
                    "specialized": {
                        "cost": {
                            "construction_cost": 58381.40474038341,
                            "maintenance_cost": 245.20189990961032,
                            "currency": "EUR",
                        }
                    },
                },
            ]
        }
    )
