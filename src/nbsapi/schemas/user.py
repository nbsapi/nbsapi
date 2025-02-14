from random import randint

from pydantic import BaseModel, ConfigDict, EmailStr, Field


def gen_example_username():
    return f"nbsapi_user_{randint(1000, 9999)}"


def gen_example_password():
    return f"nbsapi{randint(1000, 9999)}"


def gen_example_email():
    return f"user{randint(10, 9999)}@domain.com"


class UserBase(BaseModel):
    username: str = Field(
        ..., min_length=3, max_length=50, examples=[gen_example_username()]
    )
    email: EmailStr = Field(..., examples=[gen_example_email()])
    first_name: str = Field(..., examples=["Jane"])
    last_name: str = Field(..., examples=["Doe"])


class UserWrite(UserBase):
    password: str = Field(..., min_length=8, examples=[gen_example_password()])


class User(UserBase):
    model_config = ConfigDict(from_attributes=True)
    disabled: bool = Field(False, examples=[False])


class UserPrivate(User):
    hashed_password: str
