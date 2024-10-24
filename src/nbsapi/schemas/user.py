from random import randint

from pydantic import BaseModel, ConfigDict, Field


def gen_example_username():
    return f"nbsapi_user_{randint(1000,9999)}"


def gen_example_password():
    return f"nbsapi{randint(1000,9999)}"


def gen_example_email():
    return f"user{randint(10,9999)}@domain.com"


class User(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    username: str = Field(None, examples=[gen_example_username()])
    email: str = Field(None, examples=[gen_example_email()])
    first_name: str = Field(None, examples=["Jane"])
    last_name: str = Field(None, examples=["Doe"])
    disabled: bool = Field(False, examples=[False])


class UserWrite(User):
    password: str = Field(None, examples=[gen_example_password()])


class UserPrivate(User):
    hashed_password: str
