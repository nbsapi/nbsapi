from pydantic import BaseModel, ConfigDict


class Contact(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "examples": [
                {"website": "https://community.nbsapi.org"},
            ]
        },
    )

    website: str
