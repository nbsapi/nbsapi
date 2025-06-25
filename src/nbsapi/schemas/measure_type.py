"""Measure Type schemas for predefined Nature-Based Solution types."""

from pydantic import BaseModel, Field


class MeasureTypeBase(BaseModel):
    """Base schema for measure types."""

    id: str = Field(
        ...,
        description="Unique identifier for the measure type",
        examples=["39", "26", "6"],
    )
    name: str = Field(
        ...,
        description="Name of the measure type",
        examples=["Green Roof", "Rain Garden", "Bioswale"],
    )
    description: str | None = Field(None, description="Description of the measure type")
    default_color: str | None = Field(
        None,
        description="Default hex color for rendering",
        examples=["#31D336", "#cfdd20"],
    )
    default_inflow: float | None = Field(
        None,
        description="Default inflow rate in liters per second",
        examples=[1.0, 10.0],
    )
    default_depth: float | None = Field(
        None, description="Default depth in meters", examples=[0.05, 0.35]
    )
    default_width: float | None = Field(
        None, description="Default width in meters", examples=[5.0, 1.0]
    )
    default_radius: float | None = Field(
        None, description="Default radius in meters", examples=[1.0, 0.0001]
    )


class MeasureTypeCreate(MeasureTypeBase):
    """Schema for creating a measure type."""

    pass


class MeasureTypeRead(MeasureTypeBase):
    """Schema for reading a measure type."""

    pass


class MeasureTypeUpdate(BaseModel):
    """Schema for updating a measure type."""

    name: str | None = None
    description: str | None = None
    default_color: str | None = None
    default_inflow: float | None = None
    default_depth: float | None = None
    default_width: float | None = None
    default_radius: float | None = None
