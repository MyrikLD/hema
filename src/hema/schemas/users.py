from pydantic import BaseModel, ConfigDict, Field
from enum import Enum as PyEnum

class UserGender(str, PyEnum):
    MALE = "Male"
    FEMALE = "Female"
    OTHER = "Other"
    PREF_NOT_TO_TELL = "Prefer not to tell"


class UserCreateSchema(BaseModel):
    name : str
    password : str
    gender : UserGender = Field(default=UserGender.OTHER)
    phone : str

    model_config = ConfigDict(extra="forbid")

class UserCreateResponseSchema(BaseModel):
    name : str
    gender : UserGender = Field(default=UserGender.OTHER)
    phone : str

    model_config = ConfigDict(from_attributes=True)