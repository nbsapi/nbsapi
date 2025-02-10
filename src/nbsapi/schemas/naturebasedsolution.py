from pydantic import BaseModel, ConfigDict, Field

from nbsapi.schemas.adaptationtarget import (
    AdaptationTargetRead,
)
from nbsapi.schemas.impact import ImpactBase


class NatureBasedSolutionBase(BaseModel):
    name: str = Field(..., examples=["Coastal Restoration"])
    definition: str = Field(..., examples=["Definition of the solution"])
    cobenefits: str = Field(..., examples=["Improved biodiversity"])
    specificdetails: str = Field(..., examples=["Detailed information"])
    location: str = Field(..., examples=["Coastal Area X"])
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
            ]
        ],
    )


class NatureBasedSolutionCreate(NatureBasedSolutionBase):
    adaptations: list[AdaptationTargetRead] = Field(
        default_factory=list,
        description="List of adaptation types and their corresponding values",
        examples=[
            [
                {"adaptation": {"type": "Heat"}, "value": 10},
                {"adaptation": {"type": "Pluvial Flooding"}, "value": 20},
            ]
        ],
    )


class NatureBasedSolutionUpdate(BaseModel):
    name: str | None = Field(None, examples=["Riprap"])
    definition: str | None = Field(None, examples=["Updated definition"])
    cobenefits: str | None = Field(None, examples=["Enhanced ecosystem services"])
    specificdetails: str | None = Field(None, examples=["Updated detailed information"])
    location: str | None = Field(None, examples=["Updated Coastal Area Y"])
    adaptations: list[AdaptationTargetRead] | None = Field(
        None,
        description="List of adaptation types and their corresponding values",
        examples=[
            [
                {"adaptation": {"id": 1, "type": "Heat"}, "value": 10},
                {"adaptation": {"id": 2, "type": "Pluvial Flooding"}, "value": 20},
            ]
        ],
    )


class NatureBasedSolutionRead(NatureBasedSolutionBase):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)
    id: int
    adaptations: list[AdaptationTargetRead] = Field(
        alias="solution_targets",
        description="List of AdaptationTarget and their corresponding values",
        default_factory=list,
    )
