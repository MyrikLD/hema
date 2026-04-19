"""Pydantic schemas for Event API models."""

from datetime import date, time

from pydantic import BaseModel, ConfigDict, model_validator


class EventBase(BaseModel):
    """Base event schema with common fields."""

    model_config = ConfigDict(from_attributes=True)

    name: str
    color: str = "4CAF50"
    date: date
    time_start: time
    time_end: time
    weekly_id: int | None = None
    trainer_id: int | None = None
    price: int = 0


class EventResponse(EventBase):
    """Event response schema with ID."""

    id: int
    trainer_name: str | None = None


class EventCreateSchema(BaseModel):
    """Event create schema."""

    name: str
    color: str = "4CAF50"
    date: date
    time_start: time
    time_end: time
    price: int = 0

    model_config = ConfigDict(extra="forbid")

    @model_validator(mode="after")
    def validate_times(cls, values):
        if values.time_start >= values.time_end:
            raise ValueError("time_start must be before time_end")
        return values
