from pydantic import BaseModel, Field


class PhysicalProperties(BaseModel):
    """Physical properties for nature-based solutions"""

    # Default properties
    default_inflow: float | None = Field(
        None, description="Default inflow in liters per second", examples=[5.0]
    )
    default_depth: float | None = Field(
        None, description="Default depth in meters", examples=[1.5]
    )
    default_width: float | None = Field(
        None, description="Default width in meters", examples=[2.0]
    )
    default_radius: float | None = Field(
        None, description="Default radius in meters", examples=[3.5]
    )

    # Area-specific properties
    area_inflow: float | None = Field(
        None, description="Area-specific inflow in liters per second", examples=[7.2]
    )
    area_depth: float | None = Field(
        None, description="Area-specific depth in meters", examples=[2.1]
    )
    area_width: float | None = Field(
        None, description="Area-specific width in meters", examples=[3.8]
    )
    area_radius: float | None = Field(
        None, description="Area-specific radius in meters", examples=[5.0]
    )
