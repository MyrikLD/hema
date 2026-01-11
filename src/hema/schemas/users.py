from pydantic import BaseModel, ConfigDict, Field
from enum import Enum


class UserGender(str, Enum):
    MALE = "Male"
    FEMALE = "Female"
    OTHER = "Other"


class UserCreateSchema(BaseModel):
    name: str
    password: str
    gender: UserGender = UserGender.OTHER
    phone: str
    is_trainer: bool

    model_config = ConfigDict(extra="forbid")


class UserCreateResponseSchema(BaseModel):
    id: int
    name: str
    gender: UserGender = Field(default=UserGender.OTHER)
    phone: str
    is_trainer: bool

    model_config = ConfigDict(from_attributes=True)


class UserProfileUpdateShema(BaseModel):
    name: str | None = None
    phone: str | None = None

    model_config = ConfigDict(extra="forbid")


class UserProfileUpdateResponseShema(UserProfileUpdateShema):

    model_config = ConfigDict(from_attributes=True)
