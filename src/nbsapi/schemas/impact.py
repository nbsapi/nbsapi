from pydantic import BaseModel, ConfigDict, Field
from typing_extensions import Annotated


class ImpactIntensity(BaseModel):
    "Impact intensity"

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={"examples": [{"intensity": "low"}, {"intensity": "medium"}]},
    )
    intensity: str


class ImpactUnit(BaseModel):
    "Impact unit of measure"

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "examples": [
                {"unit": "m2", "description": "shade"},
                {"unit": "m3", "description": "water volume"},
            ]
        },
    )
    unit: str
    description: str


class ImpactBase(BaseModel):
    "NbS Impact"

    model_config = ConfigDict(
        from_attributes=True,
    )
    magnitude: float
    unit: ImpactUnit = Field()
    intensity: ImpactIntensity = Field()


class ImpactRead(BaseModel):
    "Impacts"

    model_config = ConfigDict(
        # json_schema_extra={"examples": [{"adaptation": {"type": "Heat"}, "value": 80}]},
        from_attributes=True,
    )

    impact: ImpactBase


# class NbsImpactCreate(ImpactBase):
#     """Write an NbS impact, Requires magnitude, intensity, and unit"""

#     id: int | None = None
#     description: str | None = None
