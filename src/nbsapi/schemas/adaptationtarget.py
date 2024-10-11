from pydantic import BaseModel, ConfigDict, Field
from typing_extensions import Annotated


class TargetBase(BaseModel):
    "A type of climate adaptation"

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "examples": [{"type": "Pluvial flooding"}, {"type": "Drought"}]
        },
    )

    type: str


class AdaptationTargetRead(BaseModel):
    "Adaptation targets are instances of `TargetBase` associated with a Nature-Based Solution, each target having an associated value 0 - 100"

    model_config = ConfigDict(
        json_schema_extra={"examples": [{"adaptation": {"type": "Heat"}, "value": 80}]},
        from_attributes=True,
    )

    adaptation: TargetBase
    value: Annotated[int, Field(ge=0, le=100)]
