from pydantic import BaseModel, Field


class StylingProperties(BaseModel):
    """Visual styling properties for NBS features"""

    color: str = Field(
        default="#3388ff",
        description="Hex color code for rendering",
        examples=["#ff0000", "#00ff00", "#0000ff"],
    )
    hidden: bool = Field(
        default=False,
        description="Whether the feature should be hidden on initial render",
    )
