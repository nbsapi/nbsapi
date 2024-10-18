from pydantic import BaseModel, ConfigDict


class ApiVersion(BaseModel):
    "The API version. `version` is a positive integer, monotonically increasing"

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={"examples": [{"version": 1}, {"version": 2}]},
    )

    version: int
