from pydantic import BaseModel, ConfigDict, Field
from typing_extensions import Annotated


class ImpactBase(BaseModel):
    "NbS Impact"

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            # "examples": [{"type": "Pluvial flooding"}, {"type": "Drought"}]
        },
    )
    id: int
    description: str
    magnitude: float
    intensity: str
    unit: str


class ImpactRead(BaseModel):
    "Impacts"

    model_config = ConfigDict(
        # json_schema_extra={"examples": [{"adaptation": {"type": "Heat"}, "value": 80}]},
        from_attributes=True,
    )

    impact: ImpactBase


class NbsImpactCreate(ImpactBase):
    """Write an NbS impact, Requires magnitude, intensity, and unit"""

    id: int | None = None
    description: str | None = None
