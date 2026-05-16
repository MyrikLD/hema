from enum import StrEnum
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class UserGender(StrEnum):
    MALE = "m"
    FEMALE = "f"
    OTHER = "o"


class UserCreateSchema(BaseModel):
    username: str
    password: str = Field(min_length=6)
    gender: UserGender = UserGender.OTHER
    phone: str | None = None


class UserResponseSchema(BaseModel):
    username: str
    name: str | None = None
    gender: UserGender = Field(default=UserGender.OTHER)
    phone: str | None = None
    is_trainer: bool = False

    model_config = ConfigDict(from_attributes=True)


class UserProfileUpdateShema(BaseModel):
    username: str | None = None
    name: str | None = None
    phone: str | None = None
    gender: UserGender | None = None
    password: str | None = Field(None, min_length=6)


class UserProfileUpdateResponseShema(UserProfileUpdateShema):
    model_config = ConfigDict(from_attributes=True)


class AuthResponseModel(BaseModel):
    access_token: str
    token_type: Literal["bearer"]
