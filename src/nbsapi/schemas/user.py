from pydantic import BaseModel, ConfigDict, Field


class User(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    username: str = Field(None, examples=["nbsapi_user"])
    email: str = Field(None, examples=["user@domain.com"])
    first_name: str = Field(None, examples=["Jane"])
    last_name: str = Field(None, examples=["Doe"])


class UserWrite(User):
    password: str = Field(None, examples=["nbsapi"])
    disabled: bool = Field(False, examples=[False])


class UserPrivate(User):
    hashed_password: str
