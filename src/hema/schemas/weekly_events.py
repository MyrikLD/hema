"""Pydantic schemas for WeeklyEvent (recurring events)."""

from datetime import date, time

from pydantic import BaseModel, ConfigDict, Field, model_validator


class WeeklyEventBase(BaseModel):
    """Base weekly event schema."""

    model_config = ConfigDict(from_attributes=True)

    start: date
    end: date
    name: str
    color: str = "4CAF50"
    weekday: int = Field(ge=0, le=6)  # 0=Monday … 6=Sunday
    time_start: time
    time_end: time
    price: int = Field(ge=0)

    @model_validator(mode="after")
    def validate_fields(cls, values):
        if values.start > values.end:
            raise ValueError("start must be before end")
        if values.time_start >= values.time_end:
            raise ValueError("time_start must be before time_end")
        return values


class WeeklyEventCreate(WeeklyEventBase):
    pass


class WeeklyEventUpdate(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    start: date | None = None
    end: date | None = None
    name: str | None = None
    color: str | None = None
    weekday: int | None = Field(None, ge=0, le=6)
    time_start: time | None = None
    time_end: time | None = None
    trainer_id: int | None = None
    price: int | None = Field(None, ge=0)


class WeeklyEventResponse(WeeklyEventBase):
    id: int
    trainer_id: int | None = None
