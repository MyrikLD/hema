from enum import StrEnum
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class UserGender(StrEnum):
    MALE = "m"
    FEMALE = "f"
    OTHER = "o"


class UserCreateSchema(BaseModel):
    name: str
    password: str
    gender: UserGender = UserGender.OTHER
    phone: str | None = None

    model_config = ConfigDict(extra="forbid")


class UserResponseSchema(BaseModel):
    name: str
    gender: UserGender = Field(default=UserGender.OTHER)
    phone: str | None = None

    model_config = ConfigDict(from_attributes=True)


class UserProfileUpdateShema(BaseModel):
    name: str | None = None
    phone: str | None = None
    gender: UserGender | None = None
    password: str | None = None

    model_config = ConfigDict(extra="forbid")


class UserProfileUpdateResponseShema(UserProfileUpdateShema):
    model_config = ConfigDict(from_attributes=True)


class AuthResponseModel(BaseModel):
    access_token: str
    token_type: Literal["bearer"]
